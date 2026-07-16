library(tidyverse)
library(glue)

train_level <- "combined"
real_base_dir <- '/l/storysem/bids/derivatives/decoding/average/source-level'

for (test_level in c("level1", "level2", "level3")) {
  for (t in list(c(100, 300), c(300, 500), c(500, 700))) {
    tmin <- t[1]
    tmax <- t[2]
    current_result <- glue(
      "{real_base_dir}/{train_level}-{test_level}_{tmin}-{tmax}_merged.csv"
    )

    allowed <- c("all", "Abstract", "Concrete", "within", "between")

    real_df <- read_csv(current_result) %>%
      mutate(
        patch = as.integer(str_match(subject, "^patch(\\d+)-")[, 2]),
        obs_id = factor("obs", levels = "obs")
      ) %>%
      filter(X %in% allowed, Y %in% allowed) %>%
      select(patch, X, Y, accuracy, obs_id)

    # order
    patch_levels <- sort(unique(real_df$patch))

    # enforce that order
    real_df <- real_df %>%
      mutate(
        patch = factor(patch, levels = patch_levels)
      )
    for (comp in list(
      c("all", "all"),
      c("Concrete", "Abstract"),
      c("Abstract", "Abstract"),
      c("Concrete", "Concrete")
    )) {
      comp1 <- comp[1]
      comp2 <- comp[2]

      df <- real_df %>%
        filter(X == comp1, Y == comp2)

      # fail if duplicates exist
      dups <- df %>% count(patch) %>% filter(n > 1)
      stopifnot(nrow(dups) == 0)

      # xtab introduces 0s if perm is missing, put NA instead
      mat <- xtabs(accuracy ~ obs_id + patch, data = df)
      #mat[mat == 0]

      Y_obs <- array(
        as.matrix(mat),
        dim = c(1, 1, length(patch_levels)),
        dimnames = list(
          perm = "obs",
          sample = "s1",
          patch = patch_levels
        )
      )

      saveRDS(
        Y_obs,
        glue(
          "{real_base_dir}/{train_level}-{test_level}_{tmin}-{tmax}_{comp1}-{comp2}_source_obs_array.rds"
        )
      )
    }
  }
}
