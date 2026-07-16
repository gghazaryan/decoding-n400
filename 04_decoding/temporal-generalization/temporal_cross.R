library(tidyverse)
library(glue)
library(viridis)
library(patchwork)
library(cowplot)
library(permuco)
library(igraph)
library(ggpattern)
library(ggfx)
library(ggpubr)

DATA_PATH <- "data/"

build_perm_mat <- function(all_perms_f, train_level_name, test_level_name) {
  all_perms <- read_csv(all_perms_f) %>%
    mutate(train_time = as.numeric(test_time)) %>%
    filter(train_level == train_level_name, test_level == test_level_name) %>%
    select(accuracy, train_time, test_time, perm) %>%
    arrange(as.numeric(train_time), as.numeric(test_time)) %>%
    select(-test_time) %>%
    pivot_wider(names_from = train_time, values_from = accuracy) %>%
    arrange(perm) %>%
    select(-perm) %>%
    as.matrix()
  return(all_perms)
}


build_real_data_mat <- function(real_data, train_level_name, test_level_name) {
  real_data %>%
    filter(train_level == train_level_name, test_level == test_level_name) %>%
    select(accuracy, train_time, test_time) %>%
    arrange(as.numeric(train_time), as.numeric(test_time)) %>%
    pivot_wider(names_from = test_time, values_from = accuracy) %>%
    arrange(train_time) %>%
    select(-train_time) %>%
    as.matrix()
}

# null for threshold
null1 <- build_perm_mat(
  paste0(DATA_PATH, '/perm_decoding.csv'),
  train_level_name = 'train-level1',
  test_level_name = 'test-level1'
)

 combined_real_df <- read_csv(paste0(DATA_PATH, "/decoding_grad.csv"))


perm_tc_df <- read_csv(paste0(
  DATA_PATH,
  '/perm_temporal_generalization.csv'
)) %>%
  select(perm, train_time, test_time, accuracy) %>%
  arrange(train_time, test_time, perm)

perm_tc_arr <- reshape2::acast(
  perm_tc_df %>%
    mutate(
      train_time = factor(train_time, 0:45),
      test_time = factor(test_time, 0:45)
    ),
  perm ~ test_time ~ train_time,
  value.var = "accuracy"
)


tt <- as.character(0:45)

# edges: 1--2, 2--3, ..., 45--46
edges <- c(rbind(tt[-length(tt)], tt[-1]))

g <- make_graph(edges, directed = FALSE)
V(g)$name <- as.character(1:46)


df_list <- list()

for (level in c('level1', 'level2', 'level3', 'combined')) {
  train_level_name <- paste0("train-", level)
  for (level2 in c('level1', 'level2', 'level3')) {
    test_level_name <- paste0("test-", level2)
    print(paste(train_level_name, test_level_name))

    current_subset <- combined_real_df %>%
      filter(train_level == train_level_name, test_level == test_level_name) %>%
      select(train_level, test_level, train_time, test_time, accuracy)

    real_arr <- reshape2::acast(
      current_subset,
      test_time ~ train_time,
      value.var = "accuracy"
    )

    merged_arr <- abind::abind(real_arr, perm_tc_arr, along = 1)

    dimnames(merged_arr) <- list(
      obs = c("obs", as.character(1:(dim(merged_arr)[1] - 1))),
      train_time = as.character(1:dim(merged_arr)[2]),
      test_time = as.character(1:dim(merged_arr)[3])
    )
    # stats

    res <- permuco4brain::compute_clustermass_array(
      distribution = merged_arr,
      # [perms+obs x 46 x 46]
      graph = g,
      alternative = "greater",
      threshold = quantile(null1, 0.95),
      aggr_FUN = sum
    )$data %>%
      as_tibble()

    res <- res %>%
      mutate(
        train_time = as.numeric(channel) - 1,
        test_time = as.numeric(sample) - 1
      ) %>%
      inner_join(current_subset)

    df_list <- append(df_list, list(res))
  }
}


tc_results_df <- do.call(rbind, df_list)


p_tbl <- tc_results_df %>%
  filter(cluster_id != 0) %>%
  group_by(train_level, test_level) %>%
  summarise(pvalue = min(pvalue), .groups = "drop") %>%
  mutate(p_fdr = p.adjust(pvalue, method = "BH")) %>%
  select(-pvalue)


tc_results_df <- tc_results_df %>%
  left_join(p_tbl, by = c("train_level", "test_level"))


lvl <- setdiff(levels(factor(tc_results_df$train_level)), "train-combined")
tc_results_df$train_level <- factor(
  tc_results_df$train_level,
  levels = c(lvl, "train-combined")
)
lvl <- levels(factor(tc_results_df$test_level))
tc_results_df$test_level <- factor(tc_results_df$test_level, levels = c(lvl))


# Get unique levels in correct order
train_levels <- c(
  "train-level1",
  "train-level2",
  "train-level3",
  "train-combined"
)
test_levels <- c("test-level1", "test-level2", "test-level3")

# Create label mapping
label_map <- c(
  "train-level1" = "Train:\nHighly related",
  "test-level1" = "Test: Highly related",
  "train-level2" = "Train:\nModerately related",
  "test-level2" = "Test: Moderately related",
  "train-level3" = "Train:\nUnrelated",
  "test-level3" = "Test: Unrelated",
  "train-combined" = "Train:\nPooled"
)

# Create a list to store plots
plot_list <- list()

for (i in seq_along(test_levels)) {
  tl <- test_levels[i]
  for (j in seq_along(train_levels)) {
    tr <- train_levels[j]

    # Create diagonal line plot
    diag_data <- tc_results_df %>%
      filter(train_level == tr, test_level == tl, train_time == test_time)

    line_plot <- ggplot(
      diag_data,
      aes(
        x = train_time * 20,
        y = accuracy *
          100
      )
    ) +
      geom_line(color = "black") +
      scale_x_continuous(expand = c(0, 0)) +
      scale_y_continuous(
        limits = c(30, 85),
        expand = c(0, 0),
        breaks = c(40, 60, 80)
      ) +
      theme_cowplot() +
      theme(
        axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.line.x = element_blank(),
        axis.ticks.x = element_blank(),
        panel.border = element_blank(),
        panel.background = element_blank(),
        plot.margin = margin(3, 3, 1, 3),
        axis.text = element_text(size = 10),
        axis.title = element_blank()
      ) +
      ylab("Accuracy (%)") +
      geom_vline(xintercept = 300, linetype = 'dashed', color = "gray") +
      geom_vline(xintercept = 500, linetype = 'dashed', color = "gray") +
      geom_hline(yintercept = 50, linetype = "dotted", color = 'gray')

    # Create heatmap for this facet
    heat_data <- tc_results_df %>%
      filter(train_level == tr, test_level == tl) %>%
      mutate(acc_plot = (if_else(accuracy < 0.5, 0.5, accuracy))) %>%
      mutate(trans = if_else(pvalue < 0.05, 1, 0.5))

    blur_df <- subset(heat_data, pvalue > 0)
    normal_df <- subset(heat_data, pvalue < 0.05)

    p <- p_tbl %>% # non-significant facets
      filter(train_level == tr, test_level == tl) %>%
      pull(p_fdr)

    alpha <- 0.05
    border_col <- ifelse(p > alpha, "black", "black")
    border_lty <- ifelse(p > alpha, "dotted", "solid")

    heat_plot <- ggplot(
      heat_data,
      aes(
        x = train_time * 20,
        y = test_time * 20,
        fill = acc_plot * 100,
        alpha = trans
      )
    ) +
      geom_tile(fill = "white", color = NA) +
      geom_tile(data = blur_df) +
      geom_tile(data = normal_df) +
      theme_cowplot() +
      scale_fill_viridis_c(
        option = "viridis",
        na.value = "grey90",
        name = "Accuracy",
        breaks = scales::breaks_extended(n = 4),
        limits = c(50, 80)
      ) +
      scale_x_continuous(
        expand = c(0, 0),
        breaks = c(100, 300, 500, 700)
      ) +
      scale_y_continuous(
        expand = c(0, 0),
        breaks = c(100, 300, 500, 700)
      ) +
      coord_equal() +
      theme(
        legend.position = "none",
        plot.margin = margin(3, 3, 1, 3),
        axis.title = element_blank(),
        axis.text = element_text(size = 10),
        panel.border = element_rect(
          colour = border_col,
          fill = NA,
          linewidth = 1.5,
          linetype = border_lty
        )
      ) +
      geom_vline(
        xintercept = 300,
        linetype = 'dashed',
        color = "gray90",
        linewidth = 0.5
      ) +
      geom_vline(
        xintercept = 500,
        linetype = 'dashed',
        color = "gray90",
        linewidth = 0.5
      ) +
      geom_hline(
        yintercept = 300,
        linetype = 'dashed',
        color = "gray90",
        linewidth = 0.5
      ) +
      geom_hline(
        yintercept = 500,
        linetype = 'dashed',
        color = "gray90",
        linewidth = 0.5
      ) +

      scale_alpha_identity()

    heat_plot
    # Add axis labels only to edge plots
    if (i == length(test_levels)) {
      heat_plot <- heat_plot +
        xlab("Train time (ms)") +
        theme(axis.title.x = element_text(size = 14))
    }
    if (j == 1) {
      heat_plot <- heat_plot +
        ylab("Test time (ms)") +
        theme(axis.title.y = element_text(size = 14))

      line_plot <- line_plot +
        ylab("Accuracy") +
        theme(axis.title.y = element_text(size = 14))
    }

    # Combine with patchwork
    combined <- line_plot / heat_plot + plot_layout(heights = c(2.5, 10))

    plot_list[[paste(i, j)]] <- combined
  }
}

# Create column titles
col_titles <- lapply(train_levels, function(x) {
  wrap_elements(grid::textGrob(label_map[x], gp = grid::gpar(fontsize = 14)))
})

# Create row titles
row_titles <- lapply(test_levels, function(x) {
  wrap_elements(grid::textGrob(
    label_map[x],
    rot = 90,
    gp = grid::gpar(fontsize = 14)
  ))
})


# Arrange plots in grid with titles
plot_matrix <- matrix(
  plot_list,
  nrow = length(test_levels),
  ncol = length(train_levels),
  byrow = TRUE
)

# Build the layout
layout <- wrap_plots(
  c(
    list(plot_spacer()),
    col_titles,
    unlist(lapply(1:length(test_levels), function(i) {
      c(list(row_titles[[i]]), plot_matrix[i, ])
    }))
  ),
  ncol = length(train_levels) + 1,
  widths = c(0.5, rep(1, length(train_levels))),
  heights = c(0.3, rep(1, length(test_levels)))
)

# Create shared legend
legend_plot <- ggplot(
  tc_results_df,
  aes(
    x = train_time * 20,
    y = test_time * 20,
    fill = accuracy * 100
  )
) +
  geom_tile() +
  scale_fill_viridis_c(
    option = "viridis",
    na.value = "grey90",
    name = "Accuracy\n ",
    breaks = scales::breaks_extended(n = 4),
    limits = c(50, 80)
  ) +
  theme_void() +
  theme(
    legend.position = "bottom",
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)
  ) +
  guides(
    fill = guide_colorbar(barwidth = unit(5, "cm"), barheight = unit(0.4, "cm"))
  )


legend <- cowplot::get_legend(legend_plot)

# Final composition
final_fig <- (layout /
  wrap_elements(legend) +
  plot_layout(heights = c(20, 1), guides = "collect")) &
  theme(
    axis.text = element_text(size = 12),
    text = element_text(size = 14),
    legend.text = element_text(size = 12)
  )

ggsave("figures/cross_decoding.pdf", final_fig, height = 11, width = 10)


stat_nums <- tc_results_df %>%
  group_by(train_level, test_level, cluster_id) %>%
  left_join(tc_results_df) %>%
  filter(pvalue < 0.05) %>%
  select(cluster_id, clustermass, pvalue, p_fdr) %>%
  group_by(cluster_id) %>%
  distinct()
