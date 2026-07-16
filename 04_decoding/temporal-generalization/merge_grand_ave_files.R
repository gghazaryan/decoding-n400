library(tidyverse)
library(sjmisc)
library(stringr)
library(glue)

for (ch_type in c("grad")) {
  df_list <- list()

  for (train_level in c('level1', 'level2', 'level3', 'combined')) {
    directory_path <- glue('data/tc_{train_level}/')

    all_files <- list.files(
      directory_path,
      pattern = glue("{ch_type}.*\\.csv$"),
      full.names = TRUE
    )

    for (test_level in c('level1', 'level2', 'level3')) {
      extracted_files <- all_files[grepl(
        glue("test_level-{test_level}"),
        all_files
      )]

      # Iterate through CSV files, read them, and append to df_list
      for (csv_file in extracted_files) {
        matches <- regmatches(
          csv_file,
          regexpr("[0-9]+(?=_tc\\.csv$)", csv_file, perl = TRUE)
        )

        train_time <- as.numeric(matches)

        data <- read_csv(csv_file) %>%
          filter(X == "all", Y == "all") %>%
          mutate(
            train_time = train_time,
            test_time = t,
            train_level = glue("train-{train_level}"),
            test_level = glue("test-{test_level}")
          )
        df_list <- append(df_list, list(data))
      }
    }
  }
  combined_df <- do.call(rbind, df_list)
  write_csv(combined_df, glue('results/tc_merged_csv/decoding_{ch_type}.csv'))
}
