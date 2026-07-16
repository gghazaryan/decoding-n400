library(tidyverse)
library(sjmisc)
library(stringr)
library(glue)

df_list <- list()

for (ch_type in c("grad")) {
  for (train_level in c('combined', 'level1', 'level2', 'level3')) {
    print(paste("Train level", train_level))

    directory_path <- glue('results/decoding_windows/perm/{train_level}')

    all_files <- list.files(
      directory_path,
      pattern = glue("{ch_type}.*\\.csv$"),
      full.names = TRUE
    )

    for (test_level in c('level1', 'level2', 'level3')) {
      print(paste("Test level", test_level))

      pattern <- glue("train_level-{train_level}_test_level-{test_level}")
      extracted_files <- all_files[grepl(pattern, all_files, fixed = TRUE)]

      # Iterate through CSV files, read them, and append to df_list
      for (csv_file in extracted_files) {
        window <- sub(".*grad-([+-]?[0-9]+).*", "\\1", csv_file)

        # Extract perm number
        perm_num <- sub(".*_perm-([+-]?[0-9]+).*", "\\1", csv_file)

        data <- read_csv(csv_file, show_col_types = FALSE) %>%
          filter(X == "all", Y == "all") %>%
          mutate(
            w = window,
            ch = ch_type,
            train_l = train_level,
            test_l = test_level,
            perm = perm_num
          )
        df_list <- append(df_list, list(data))
      }
    }
  }
}

combined_df_perm <- do.call(rbind, df_list)
write_csv(
  combined_df_perm,
  glue(
    'data/decoding_windows/perm_merged_decoding_windows_train-{train_level}_{ch_type}.csv'
  )
)
