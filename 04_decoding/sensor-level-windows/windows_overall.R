library(tidyverse)
library(sjmisc)
library(stringr)
library(glue)
library(cowplot)
library(qvalue)
library(patchwork)

DATA_PATH <- "data/decoding_windows/"

df_list <- list()

for (ch_type in c("grad")) {
  for (train_level in c('level1', 'level2', 'level3', 'combined')) {
    all_files <- list.files(
      DATA_PATH,
      pattern = glue("{ch_type}.*\\.csv$"),
      full.names = TRUE
    )

    for (test_level in c('level1', 'level2', 'level3')) {
      pattern <- glue("train_level-{train_level}_test_level-{test_level}")

      extracted_files <- all_files[grepl(pattern, all_files, fixed = TRUE)]

      # Iterate through CSV files, read them, and append to df_list
      for (csv_file in extracted_files) {
        matches <- regmatches(
          csv_file,
          regexpr("[0-9]+(?=_window\\.csv$)", csv_file, perl = TRUE)
        )

        window <- as.numeric(matches)

        data <- read_csv(csv_file) %>%
          filter(X == "all", Y == "all") %>%
          mutate(
            w = window,
            ch = ch_type,
            train_l = train_level,
            test_l = test_level
          )

        df_list <- append(df_list, list(data))
        extracted_files <- NA
      }
    }
  }
}

combined_df <- do.call(rbind, df_list)


trained_same_df_perm <- read_csv(paste0(
  DATA_PATH,
  "/merged_csvs/perm_merged_decoding_windows_train-same_grad.csv"
))

trained_pooled_df_perm <- read_csv(paste0(
  DATA_PATH,
  "/merged_csvs/perm_merged_decoding_windows_train-pooled_grad.csv"
))


calc_p_vs_chance <- function(observed_df, perm_df, test_level, window) {
  null_dist <- perm_df %>%
    filter(
      test_l == "level1",
      ch == "grad"
    ) %>%
    pull(accuracy)

  observed <- observed_df %>%
    filter(test_l == test_level, w == window, ch == "grad") %>%
    pull(accuracy)

  tibble(
    test_l = test_level,
    window = window,
    p = empPvals(observed, null_dist)
  )
}

calc_p_diff <- function(
  observed_df,
  perm_df,
  test_level_higher,
  window_higher,
  test_level_lower,
  window_lower
) {
  null_dist_higher <- perm_df %>%
    filter(test_l == test_level_higher, w == 2, ch == "grad") %>%
    pull(accuracy)

  null_dist_lower <- perm_df %>%
    filter(test_l == test_level_lower, w == 1, ch == "grad") %>%
    pull(accuracy)

  null_dist_diff <- null_dist_higher - null_dist_lower
  observed_higher <- observed_df %>%
    filter(test_l == test_level_higher, w == window_higher, ch == "grad") %>%
    pull(accuracy)

  observed_lower <- observed_df %>%
    filter(test_l == test_level_lower, w == window_lower, ch == "grad") %>%
    pull(accuracy)

  observed_diff <- observed_higher - observed_lower
  p <- empPvals(observed_diff, null_dist_diff)
  if (p > 0.5) {
    p <- empPvals(-observed_diff, -null_dist_diff)
  }

  tibble(
    test_l_higher = test_level_higher,
    window_higher = window_higher,
    test_l_lower = test_level_lower,
    window_lower = window_lower,
    p = p
  )
}


make_plot <- function(observed_df, perm_df, pooled = FALSE) {
  p_vals_vs_chance <- tibble()

  if (pooled) {
    observed_df <- observed_df %>%
      filter(train_l == "combined")
    perm_df <- perm_df %>%
      filter(train_l == "combined")
  } else {
    observed_df <- observed_df %>%
      filter(train_l != "combined")
  }

  test_levels <- c("level1", "level2", "level3")

  for (test_level in test_levels) {
    for (window in c(0, 1, 2)) {
      p_vals_vs_chance <- bind_rows(
        p_vals_vs_chance,
        calc_p_vs_chance(observed_df, perm_df, test_level, window)
      )
    }
  }

  p_vals_diff_within_windows <- tibble()

  for (window in c(0, 1, 2)) {
    p_vals_diff_within_windows <- bind_rows(
      p_vals_diff_within_windows,
      calc_p_diff(
        observed_df,
        perm_df,
        test_level_higher = "level3",
        test_level_lower = "level2",
        window_higher = window,
        window_lower = window
      ),
      calc_p_diff(
        observed_df,
        perm_df,
        test_level_higher = "level2",
        test_level_lower = "level1",
        window_higher = window,
        window_lower = window
      )
    )
  }

  p_vals_diff_within_levels <- tibble()
  for (level in c("level1", "level2", "level3")) {
    p_vals_diff_within_levels <- bind_rows(
      p_vals_diff_within_levels,
      calc_p_diff(
        observed_df,
        perm_df,
        test_level_higher = level,
        test_level_lower = level,
        window_higher = 0,
        window_lower = 1
      ),
      calc_p_diff(
        observed_df,
        perm_df,
        test_level_higher = level,
        test_level_lower = level,
        window_higher = 1,
        window_lower = 2
      )
    )
  }

  # FDR correct
  stat_df <- bind_rows(
    p_vals_diff_within_levels,
    p_vals_diff_within_windows,
    p_vals_vs_chance
  ) %>%
    mutate(
      p_adj = p.adjust(p, method = "fdr"),
      p_name = if_else(p_adj < 0.05, "sig", "nonsig"),
      w = window
    )

  stat_chance_df <- stat_df %>%
    filter(!is.na(test_l)) %>%
    select(test_l, w, p_adj, p_name, p)
  stat_diff_df <- stat_df %>% filter(!is.na(test_l_higher)) %>% select(-test_l)

  print(stat_chance_df |> select(-p_name))
  print(stat_diff_df |> select(-p_name, -window))

  # --- base data (points) ---
  dfp <- observed_df %>%
    inner_join(stat_chance_df) %>%
    filter(ch == "grad") %>%
    mutate(
      test_l = factor(test_l),
      w_str = factor(
        w,
        levels = c(0, 1, 2),
        labels = c("100-300", "300-500", "500-700")
      ),
      fill_grp = if_else(p_name == "sig", as.character(test_l), "nonsig"),
      fill_grp = factor(fill_grp, levels = c("nonsig", levels(test_l)))
    )

  pal <- setNames(
    c('#66C5B7', '#EDAE49', '#8E6C8A')[seq_len(nlevels(dfp$test_l))],
    levels(dfp$test_l)
  )

  seg <- stat_diff_df %>%
    transmute(
      level = test_l_higher,
      w_lo_str = factor(
        window_lower,
        levels = c(0, 1, 2),
        labels = c("100-300", "300-500", "500-700")
      ),
      w_hi_str = factor(
        window_higher,
        levels = c(0, 1, 2),
        labels = c("100-300", "300-500", "500-700")
      ),
      p_name
    ) %>%
    left_join(
      dfp %>% select(test_l, w_str, accuracy),
      by = c("level" = "test_l", "w_lo_str" = "w_str")
    ) %>%
    rename(y_lo = accuracy) %>%
    left_join(
      dfp %>% select(test_l, w_str, accuracy),
      by = c("level" = "test_l", "w_hi_str" = "w_str")
    ) %>%
    rename(y_hi = accuracy) %>%
    filter(!is.na(y_lo), !is.na(y_hi)) %>%
    mutate(level = factor(level, levels = levels(dfp$test_l)))

  ggplot(
    dfp,
    aes(
      x = w_str,
      y = accuracy,
      color = test_l,
      group = test_l,
      fill = fill_grp
    )
  ) +
    geom_segment(
      data = seg,
      aes(
        x = w_lo_str,
        xend = w_hi_str,
        y = y_lo,
        yend = y_hi,
        color = level,
        linetype = p_name
      ),
      linewidth = 0.6,
      inherit.aes = FALSE
    ) +
    geom_point(shape = 21, size = 3) +
    theme_cowplot() +
    ylab("Accuracy") +
    xlab("Time window (ms)") +
    theme(
      strip.background = element_blank(),
      strip.text = element_blank(),
      legend.position = "left",
      panel.grid.major.x = element_blank(),
      panel.grid.major.y = element_line(
        linewidth = 0.3,
        colour = "#D7DBE0",
        linetype = 2
      ),
      panel.grid.minor.y = element_line(
        linewidth = 0.3,
        colour = "#D7DBE0",
        linetype = 2
      )
    ) +
    scale_color_manual(
      values = pal,
      labels = c("Highly related", "Moderately related", "Unrelated"),
      name = "Relatedness level"
    ) +
    scale_fill_manual(
      values = c(nonsig = "white", pal),
      breaks = c("nonsig", levels(dfp$test_l)[1]),
      # use one filled example only
      labels = c(
        "Not significantly better than chance",
        "Significantly better than chance"
      ),
      name = NULL
    ) +
    scale_linetype_manual(
      name = NULL,
      values = c(sig = "solid", nonsig = "22"),
      labels = c(
        sig = "Significant difference",
        nonsig = "Non-significant difference"
      )
    ) +
    scale_y_continuous(
      breaks = c(0.4, 0.5, 0.6, 0.7, 0.8),
      labels = c(40, 50, 60, 70, 80),
      limits = c(0.4, 0.85)
    ) +
    guides(
      color = guide_legend(order = 1, override.aes = list(shape = 19)),
      fill = guide_legend(
        order = 2,
        override.aes = list(
          fill = c("white", "black"),
          colour = c("black", "black"),
          shape = c(21, 21)
        )
      ),
      linetype = guide_legend(order = 3)
    )
}


same_plot <- make_plot(combined_df, trained_same_df_perm, pooled = FALSE)


# stats
same_plot@data |>
  select(-subject, -t, -n_comparisons, -ch, -X, -Y)


pooled_plot <- make_plot(combined_df, trained_pooled_df_perm, pooled = TRUE)


# stats
pooled_plot@data |>
  select(-subject, -t, -n_comparisons, -ch, -X, -Y)

full_plot <- (same_plot +
  pooled_plot +
  plot_layout(axis_titles = "collect", guides = "collect")) &
  theme(
    legend.position = "bottom",
    axis.text = element_text(size = 18),
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    legend.box = "vertical",
    legend.title = element_blank()
  )

ggsave("figures/decoding_windows.pdf", full_plot, height = 6, width = 11)
