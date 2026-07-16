library(tidyverse)
library(arrow)
library(glue)
library(progress)

# variables and dirs
perm_base_dir <- "data/source-level/perm"
train_level <- "combined"
test_level <- "level3"
tmin <- 300
tmax <- 500

in_dir <- glue("{perm_base_dir}/{train_level}-{test_level}/{tmin}-{tmax}")
out_dir <- glue("{in_dir}/parquet_out")

if (!dir.exists(out_dir)) {
  dir.create(out_dir, recursive = TRUE)
}

files <- list.files(in_dir, pattern = "\\.csv$", full.names = TRUE)

# in case missing vertices due to cluster node failures
# missing_vtx <- c()
# files <- file.path(in_dir, glue("patch{missing_vtx}_combined-level3_300-500_merged.csv"))

# some repeated headers
hdr <- names(read_csv(files[1], n_max = 0, show_col_types = FALSE))
allowed <- c("all", "Abstract", "Concrete", "within", "between")

pb <- progress_bar$new(
  format = "[:bar] :current/:total (:percent) eta: :eta | :file",
  total = length(files),
  clear = FALSE,
  width = 60
)

for (f in files) {
  pb$tick(tokens = list(file = basename(f)))
  if (file.info(f)$size == 0) {
    next
  }

  df <- read_csv(f, show_col_types = FALSE) %>%
    mutate(subject = sub("\\.mat$", "", subject)) %>%
    filter(.data[[hdr[1]]] != hdr[1], X %in% allowed, Y %in% allowed) %>%
    separate(
      subject,
      into = c("patch", "permutation"),
      sep = "-",
      convert = TRUE
    )

  write_parquet(df, file.path(out_dir, paste0(basename(f), ".parquet")))
}
