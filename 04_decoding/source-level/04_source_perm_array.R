library(arrow)
library(tidyverse)
library(glue)


perm_base_dir <- "data/source-level/perm"
train_level <- "combined"
test_level <- "level3"
tmin <- 300
tmax <- 500

in_dir <- glue("{perm_base_dir}/{train_level}-{test_level}/{tmin}-{tmax}")
parquet_dir <- glue("{in_dir}/parquet_out")

files <- sort(list.files(
  parquet_dir,
  pattern = "\\.parquet$",
  full.names = TRUE
))
ds <- open_dataset(parquet_dir)


for (comp in list(
  c("all", "all"),
  c("Concrete", "Abstract"),
  c("Abstract", "Abstract"),
  c("Concrete", "Concrete")
)) {
  print(comp)
  comp1 <- comp[1]
  comp2 <- comp[2]

  df <- ds %>%
    filter(X == comp1, Y == comp2) %>%
    filter(permutation %in% c(1:500)) %>%
    select(permutation, patch, accuracy, X, Y) %>%
    collect() %>%
    mutate(
      permutation = as.integer(permutation),
      patch = as.integer(patch),
      accuracy = as.numeric(accuracy)
    )

  # order
  perm_levels <- sort(unique(df$permutation))
  patch_levels <- sort(unique(df$patch))

  # enforce that order
  df <- df %>%
    mutate(
      permutation = factor(permutation, levels = perm_levels),
      patch = factor(patch, levels = patch_levels)
    )

  # fail if duplicates exist
  dups <- df %>% count(permutation, patch) %>% filter(n > 1)
  stopifnot(nrow(dups) == 0)

  # xtab introduces 0s if perm is missing, put NA instead
  mat <- xtabs(accuracy ~ permutation + patch, data = df)

  Y <- array(
    mat,
    dim = c(nrow(mat), 1, ncol(mat)),
    dimnames = list(
      perm = as.character(perm_levels),
      sample = "s1",
      patch = as.character(patch_levels)
    )
  )

  saveRDS(
    Y,
    glue(
      "{perm_base_dir}/{train_level}-{test_level}_{tmin}-{tmax}_{comp1}-{comp2}_source_perm_array.rds"
    )
  )
}
