library(tidyverse)
library(sjmisc)
library(stringr)
library(glue)

for (ch_type in c("grad")) {
  for (train_level in c('level1')) {
    print(paste("Train level", train_level))
    df_list <- list()

    directory_path <- glue(
      '/l/storysem/bids/derivatives/decoding/average/highpass-0.1_lowpass-40/tc_{train_level}/perm'
    )

    all_files <- list.files(
      directory_path,
      pattern = glue("{ch_type}.*\\.csv$"),
      full.names = TRUE
    )

    for (test_level in c('level1', 'level2', 'level3')) {
      print(paste("Test level", test_level))
      extracted_files <- all_files[grepl(
        glue("test_level-{test_level}"),
        all_files
      )]

      # Iterate through CSV files, read them, and append to df_list
      for (csv_file in extracted_files) {
        train_time <- sub(".*grad-([+-]?[0-9]+).*", "\\1", csv_file)

        # Extract perm number after "tc_perm-"
        perm_num <- sub(".*tc_perm-([+-]?[0-9]+).*", "\\1", csv_file)

        data <- read_csv(csv_file, show_col_types = FALSE) %>%
          filter(X == "all", Y == "all") %>%
          #filter(X %in% c("Concrete","Abstract"), Y %in% c("Concrete","Abstract"),) %>%
          #mutate(comp = paste0(X,"-",Y)) %>%
          mutate(
            train_time = train_time,
            test_time = t,
            train_level = glue("train-{train_level}"),
            test_level = glue("test-{test_level}"),
            perm = perm_num
          )
        df_list <- append(df_list, list(data))
      }
    }
    combined_df <- do.call(rbind, df_list)
    write_csv(
      combined_df,
      glue(
        '/l/storysem/bids/derivatives/decoding/average/highpass-0.1_lowpass-40/tc_merged_csv/perm_decoding_tc_{train_level}_{ch_type}.csv'
      )
    )
  }
}
