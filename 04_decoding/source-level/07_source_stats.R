library(tidyverse)
library(glue)
library(permuco4brain)
library(igraph)

edges <- read_csv("data/src_edges.csv")
verts <- read_csv("data/src_vertices.csv")

train_level <- "combined"

perm_base_dir <- "data/source-level/perm"
real_base_dir <- "data/source-level"

for (comp in list(
  c("all", "all"),
  c("Concrete", "Abstract"),
  c("Abstract", "Abstract"),
  c("Concrete", "Concrete")
)) {
  comp1 <- comp[1]
  comp2 <- comp[2]
  Y_perm <- readRDS(
    glue(
      "{perm_base_dir}/combined-level3_300-500_{comp1}-{comp2}_source_perm_array.rds"
    )
  )
  edge_names <- unique(c(edges$from, edges$to))
  bad_names <- setdiff(edge_names, dimnames(Y_perm)[[3]])

  g <- graph_from_data_frame(
    edges,
    vertices = dimnames(Y_perm)[[3]],
    directed = FALSE
  )

  mu <- apply(Y_perm, c(2, 3), mean) # dim 1 x 5124
  sdv <- apply(Y_perm, c(2, 3), sd)

  Y_perm_scaled <- sweep(Y_perm, c(2, 3), mu, "-")
  Y_perm_scaled <- sweep(Y_perm_scaled, c(2, 3), sdv, "/")

  hist(
    Y_perm,
    xlab = comp,
    ylab = mean(quantile(Y_perm_scaled, 0.95) * sdv + mu)
  )

  print(comp)
  all_df <- list()
  count <- 1
  for (test_level in c("level1", "level2", "level3")) {
    for (t in list(c(100, 300), c(300, 500), c(500, 700))) {
      print(t)
      tmin <- t[1]
      tmax <- t[2]

      Y_obs <- readRDS(
        glue(
          "{real_base_dir}/{train_level}-{test_level}_{tmin}-{tmax}_{comp1}-{comp2}_source_obs_array.rds"
        )
      )

      # make sure sample + patch dimensions match
      stopifnot(identical(dim(Y_obs)[2:3], dim(Y_perm)[2:3]))

      Y_obs_scaled <- sweep(Y_obs, c(2, 3), mu, "-")
      Y_obs_scaled <- sweep(Y_obs_scaled, c(2, 3), sdv, "/")

      Y_all <- array(
        NA_real_,
        dim = c(dim(Y_perm)[1] + 1, dim(Y_perm)[2], dim(Y_perm)[3]),
        dimnames = list(
          perm = c("obs", dimnames(Y_perm)[[1]]),
          sample = dimnames(Y_perm)[[2]],
          patch = 1:5124
        )
      )

      Y_all[1, , ] <- Y_obs_scaled[1, , ]
      Y_all[2:(dim(Y_perm)[1] + 1), , ] <- Y_perm_scaled

      res <- compute_clustermass_array(
        distribution = Y_all,
        threshold = quantile(Y_perm_scaled, 0.95),
        graph = g,
        # igraph adjacency
        alternative = "greater",
        aggr_FUN = sum # cluster mass
      )$cluster

      df_membership <- data.frame(
        idx = as.integer(sub(
          "_.*$",
          "",
          names(
            res$membership
          )
        )),
        membership = res$membership,
        row.names = NULL
      )

      if (length(res$pvalue) == 0) {
        message("No p-values returned; skipping.")
        out <- data.frame(pval = numeric(0), membership = integer(0))
      } else {
        out <- data.frame(
          pval = res$pvalue,
          mass = res$clustermass,
          membership = seq_along(res$pvalue)
        )
      }
      df_pval <- out

      df_stats <- df_membership %>%
        left_join(df_pval, by = "membership") %>%
        mutate(test_level = test_level, tmin = tmin, tmax = tmax)

      all_df[[count]] <- df_s
      tats
      count <- count + 1
    }
  }

  all_df <- bind_rows(all_df)

  df_list <- all_df %>%
    group_by(membership, test_level, tmin, tmax) %>%
    summarise(
      verts = paste(idx, collapse = ","),
      mass = unique(mass),
      pval = unique(pval)
    )

  p_tbl <- df_list %>%
    group_by(test_level, tmin, tmax) %>%
    summarise(pval = min(pval), .groups = "drop") %>%
    mutate(p_fdr = p.adjust(pval, method = "BH")) %>%
    select(-pval)

  df_list <- df_list %>%
    left_join(p_tbl)

  write_csv(df_list, glue("results/source_stats_{comp1}-{comp2}_results.csv"))
}

comp1 <- "all"
comp2 <- "all"
df <- read_csv(glue("results/source_stats_{comp1}-{comp2}_results.csv"))

df %>%
  group_by(test_level, tmin, tmax) %>%
  summarise(ptest = min(p_fdr))
