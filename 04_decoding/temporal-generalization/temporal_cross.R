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


saveRDS(tc_results_df, paste0(DATA_PATH, "tc_results.RDS"))