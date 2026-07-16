library(tidyverse)
library(car)
library(lmerTest)
library(emmeans)
library(directlabels)
library(alphahull)

DATA_PATH <- "data/"

df <- read_csv(paste0(DATA_PATH, "stimuli_info_detailed.csv"))

df_filter_target <- df %>%
  select(target, target_en, target, target_nletters, target_freq) %>%
  distinct()

colnames(df_filter_target) <- c(
  "Target word",
  "Translation",
  "Length",
  "Frequency"
)

summary <- df_filter_target %>%
  summarise(across(
    where(is.numeric),
    list(
      mean = ~ mean(.x, na.rm = TRUE),
      sd = ~ sd(.x, na.rm = TRUE),
      min = ~ min(.x, na.rm = TRUE),
      max = ~ max(.x, na.rm = TRUE),
      q25 = ~ quantile(.x, 0.25, na.rm = TRUE),
      median = ~ quantile(.x, 0.50, na.rm = TRUE),
      q75 = ~ quantile(.x, 0.75, na.rm = TRUE)
    )
  ))

# FREQUENCY
df_freq_long <- df %>%
  pivot_longer(
    cols = c(prime1_freq, prime2_freq),
    names_to = "prime",
    values_to = "freq"
  )

for (choice in 1:2) {
  current_fig <- ggplot(
    df_freq_long %>% filter(prime == paste0("prime", choice, "_freq")),
    aes(x = factor(target_en, levels = unique(target_en)), y = freq)
  ) +
    stat_summary(
      fun.data = mean_se,
      geom = "pointrange",
      size = 0.1,
      linewidth = 0.1
    ) +
    labs(
      x = "Target word",
      y = paste("Frequency", paste0("(Prime", choice, ")"))
    ) +
    facet_grid(
      prime ~ relatedness_level,
      labeller = labeller(
        relatedness_level = \(x) stringr::str_to_sentence(x)
      )
    ) +
    theme_classic() +
    theme(
      axis.text.x = element_text(angle = 90),
      strip.background.y = element_blank(),
      strip.text.y = element_blank(),
      text = element_text(size = 10),
    ) +
    scale_y_log10(
      labels = scales::label_number(
        scale_cut = scales::cut_short_scale(),
        guide = guide_axis_logticks()
      )
    ) +
    coord_flip()

  ggsave(
    paste0("figures/", "prime_", choice, "_freq.pdf"),
    current_fig,
    height = 8,
    width = 6
  )
}

# NUMBER of LETTERS

df_letters_long <- df %>%
  pivot_longer(
    cols = c(prime1_nletters, prime2_nletters),
    names_to = "prime",
    values_to = "nletter"
  )

for (choice in 1:2) {
  current_fig <- ggplot(
    df_letters_long %>% filter(prime == paste0("prime", choice, "_nletters")),
    aes(x = factor(target_en, levels = unique(target_en)), y = nletter)
  ) +
    stat_summary(
      fun.data = mean_se,
      geom = "pointrange",
      size = 0.1,
      linewidth = 0.1
    ) +
    labs(
      x = "Target word",
      y = paste("Length", paste0("(Prime", choice, ")"))
    ) +
    facet_grid(
      prime ~ relatedness_level,
      labeller = labeller(
        relatedness_level = \(x) stringr::str_to_sentence(x)
      )
    ) +
    theme_classic() +
    theme(
      axis.text.x = element_text(angle = 90),
      strip.background.y = element_blank(),
      strip.text.y = element_blank()
    ) +
    coord_flip()

  ggsave(
    paste0("figures/", "prime_", choice, "_length.pdf"),
    current_fig,
    height = 8,
    width = 6
  )
}

# stats
df$prime1_freq <- scale(df$prime1_freq)
df$prime2_freq <- scale(df$prime2_freq)

m_p1_freq <- lmer(prime1_freq ~ relatedness_level + (1 | target), data = df)
m_p2_freq <- lmer(prime2_freq ~ relatedness_level + (1 | target), data = df)

m_p1_len <- lmer(prime1_nletters ~ relatedness_level + (1 | target), data = df)
m_p2_len <- lmer(prime2_nletters ~ relatedness_level + (1 | target), data = df)


anova(m_p1_freq)
anova(m_p2_freq)
anova(m_p1_len)
anova(m_p2_len)


m_p1_rel <- lmer(prime1_to_target ~ relatedness_level + (1 | target), data = df)
m_p2_rel <- lmer(prime2_to_target ~ relatedness_level + (1 | target), data = df)
m_p1_p2 <- lmer(prime1_to_prime2 ~ relatedness_level + (1 | target), data = df)
anova(m_p1_rel)
anova(m_p2_rel)
anova(m_p1_p2)

emmeans(m_p1_rel, pairwise ~ relatedness_level, adjust = "holm")
emmeans(m_p2_rel, pairwise ~ relatedness_level, adjust = "holm")
emmeans(m_p1_p2, pairwise ~ relatedness_level, adjust = "holm")

distance_fig <- df %>%
  ggplot(aes(
    x = prime1_to_target,
    y = prime2_to_target,
    color = relatedness_level
  )) +
  geom_point() +
  xlab("Prime 1 to target distance") +
  ylab("Prime 2 to target distance") +
  theme_linedraw() +
  theme(panel.grid = element_blank()) +
  directlabels::geom_dl(
    method = list("ahull.grid", cex = 0.8),
    aes(label = stringr::str_to_sentence(as.character(relatedness_level)))
  ) +
  coord_equal() +
  scale_color_manual(
    values = c('#66C5B7', '#EDAE49', '#8E6C8A'),
    guide = "none"
  ) +
  theme(text = element_text(size = 8))


ggsave("figures/stimuli_distance.pdf", distance_fig, height = 5, width = 5)
