library(tidyverse)
library(cowplot)
library(ggpubr)
library(scales)
library(ggh4x)
library(readr)
library(dplyr)
library(ggforce)
library(patchwork)

DATA_PATH <- "data/"

df <- read_csv(paste0(DATA_PATH, "/grandave_evokeds_rms.csv"))


n400_df <- df %>%
  filter(between(time, 300, 500)) %>%
  group_by(roi, level, item) %>%
  summarise(m = mean(rms))


all_pairs <- list()

for (reg in unique(n400_df$roi)) {
  d <- subset(df, roi == reg)

  # Repeated-measures ANOVA over items
  a <- afex::aov_ez(
    id = "item",
    dv = "rms",
    within = "level",
    data = d,
    type = 3
  )
  print(reg)
  print(a)

  res <- residuals(a$lm) # linear-model residuals

  em <- emmeans::emmeans(a, ~level)
  ph <- pairs(em, adjust = "none")
  tab <- as.data.frame(ph) |>
    mutate(area = reg, .before = 1)
  all_pairs[[reg]] <- tab
}

pairs_tbl <- bind_rows(all_pairs)

pairs_tbl <- pairs_tbl %>%
  mutate(p_fdr = p.adjust(p.value, method = "BH"))

pairs_tbl[, c("area", "contrast", "p.value", "p_fdr")]


max_y_values <- n400_df %>%
  group_by(roi) %>%
  summarize(max_y = max(m, na.rm = TRUE)) %>%
  ungroup()

annotation_data <- pairs_tbl %>%
  mutate(
    level1 = sapply(strsplit(contrast, " - "), `[`, 1),
    level2 = sapply(strsplit(contrast, " - "), `[`, 2)
  ) %>%
  select(area, level1, level2, p_fdr) %>%
  rename(roi = area, group1 = level1, group2 = level2) %>%
  mutate(
    label = case_when(
      p_fdr < 0.001 ~ "***",
      p_fdr < 0.01 ~ "**",
      p_fdr < 0.05 ~ "*",
      TRUE ~ ""
    )
  ) %>%
  left_join(max_y_values, by = c("roi")) %>%
  group_by(roi) %>%
  mutate(y.position = max_y * 0.86 + row_number()) %>%
  ungroup() %>%
  filter(p_fdr < 0.05)

lay <- read_csv(
  paste0(DATA_PATH, "grad_layout_2d.csv"),
  show_col_types = FALSE
) |>
  mutate(ch_key = gsub("\\s+", "", ch_name))

cx <- median(lay$x)
cy <- median(lay$y)
lay <- lay |>
  mutate(xp = x - cx, yp = y - cy)

lay <- lay |> mutate(xp = xp * 0.96, yp = yp * 0.96)

d <- sqrt(lay$xp^2 + lay$yp^2)
r <- as.numeric(quantile(d, 0.4))
pad <- 0.5 * r
lims <- c(-r - pad, r + pad)

# --- ROIs ---
read_roi <- function(path, label) {
  tibble::tibble(ROI = label, ch_name = readLines(path)) |>
    filter(ch_name != "") |>
    mutate(ch_key = gsub("\\s+", "", ch_name))
}
rois <- dplyr::bind_rows(
  read_roi(paste0(DATA_PATH, "roi_left_frontal.txt"), "Left frontal"),
  read_roi(paste0(DATA_PATH, "roi_left_parietal.txt"), "Left parietal"),
  read_roi(paste0(DATA_PATH, "roi_left_temporal.txt"), "Left temporal")
)
roi_pts <- rois |> inner_join(lay, by = "ch_key") |> select(ROI, xp, yp)

nose <- tibble::tibble(
  x = c(-0.06 * r, 0, 0.06 * r),
  y = c(1.00 * r, 1.08 * r, 1.00 * r)
)

ears <- tibble::tibble(
  x = c(-1.02 * r, 1.02 * r),
  # start point (top) L, R
  y = c(0.12 * r, -0.12 * r),
  # NOTE: right ear starts at bottom
  xend = c(-1.02 * r, 1.02 * r),
  # end point (bottom) L, R
  yend = c(-0.12 * r, 0.12 * r),
  # NOTE: right ear ends at top (swapped)
  curvature = c(-0.6, -0.6) # same bend; swapping start/end mirrors it
)


sensor_plot <- ggplot(roi_pts, aes(xp, yp)) +
  geom_circle(
    data = data.frame(x0 = 0, y0 = 0, r = r),
    aes(x0 = x0, y0 = y0, r = r),
    size = 0.5,
    fill = NA,
    inherit.aes = FALSE
  ) +
  geom_curve(
    data = ears,
    aes(
      x = x,
      y = y,
      xend = xend,
      yend = yend
    ),
    linewidth = 0.6,
    lineend = "round",
    inherit.aes = FALSE
  ) +
  geom_polygon(
    data = nose,
    aes(x, y),
    colour = "black",
    fill = NA,
    linewidth = 0.7,
    inherit.aes = FALSE
  ) +
  geom_point(size = 2) +
  coord_equal(
    xlim = lims,
    ylim = lims,
    expand = FALSE,
    clip = "off"
  ) +
  facet_wrap(~ROI, ncol = 1, strip.position = "left") +
  theme_minimal(base_size = 12) +
  theme(
    panel.grid = element_blank(),
    axis.title = element_blank(),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    strip.placement = "outside",
    panel.spacing.y = unit(75, "pt"),
    strip.text.y.right = element_text(angle = 90),
    strip.text = element_text(size = 18),
    strip.switch.pad.wrap = unit(14, "pt")
  ) +
  theme(plot.margin = margin(0, -8, 0, 0))

evokeds_plot <- df %>%
  filter(between(time, -100, 1000)) %>%
  group_by(roi, level, time) %>%
  summarise(m = mean(rms), se = sd(rms) / sqrt(n())) %>%
  ggplot(aes(x = time, y = m, color = level)) +
  geom_ribbon(
    aes(
      ymin = m - se,
      ymax = m + se,
      fill = level
    ),
    alpha = 0.5,
    color = NA
  ) +
  geom_line() +
  facet_wrap(~roi, scales = "free_y", ncol = 1, strip.position = "left") +
  theme_cowplot() +
  ylab("fT/cm") +
  xlab("Time (ms)") +
  scale_color_manual(
    values = c('#66C5B7', '#EDAE49', '#8E6C8A'),
    labels = c("Highly related", "Moderately related", "Unrelated")
  ) +
  scale_fill_manual(
    values = c('#66C5B7', '#EDAE49', '#8E6C8A'),
    labels = c("Highly related", "Moderately related", "Unrelated")
  ) +
  theme(
    strip.background = element_blank(),
    panel.spacing = unit(12, "pt"),
    legend.position = "bottom",
    strip.text = element_blank(),
    legend.title = element_blank(),
    axis.text = element_text(size = 18)
  ) +
  geom_vline(xintercept = 300, linetype = 'dashed', color = "gray") +
  geom_vline(xintercept = 500, linetype = 'dashed', color = "gray") +
  theme(
    legend.position = "bottom",
    legend.box = "horizontal",
    legend.justification = "center",
    legend.box.just = "center"
  ) +
  theme(plot.margin = margin(0, 0, 0, -200)) +
  scale_x_continuous(breaks = c(0, 200, 400, 600, 800))

n400_boxplot <- n400_df %>%
  ggplot(aes(x = level, y = m, colour = level)) +
  geom_boxplot() +
  theme_cowplot() +
  facet_wrap(~roi, ncol = 1, scales = "free_y", strip.position = "left") +
  stat_pvalue_manual(annotation_data, size = 7) +
  scale_color_manual(
    values = c('#66C5B7', '#EDAE49', '#8E6C8A'),
    labels = c("Highly related", "Moderately related", "Unrelated"),
    name = NULL
  ) +
  theme(
    axis.ticks.x = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_text(size = 18),
    strip.background = element_blank(),
    strip.text = element_blank(),
    legend.title = element_blank()
  ) +
  ylab("") +
  xlab("300-500 ms")

fig <- (sensor_plot +
  evokeds_plot +
  n400_boxplot +
  guides(color = "none") +
  plot_layout(widths = c(0.25, 0.5, 0.2), guides = "collect")) &
  theme(
    legend.position = "bottom",
    text = element_text(size = 18),
    legend.text = element_text(size = 18)
  )

ggsave(
  "figures/evoked_responses.pdf",
  fig,
  height = 9.5,
  width = 11,
  bg = "white"
)
