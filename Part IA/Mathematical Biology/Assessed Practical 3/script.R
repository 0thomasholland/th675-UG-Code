library(stringr)

semi_global <- function(str1, str2, score_match, score_mismatch, score_gap) {
  seq1 <- str_split(str1, "")[[1]]
  seq2 <- str_split(str2, "")[[1]]

  matrix_row <- length(seq1) + 1
  matrix_col <- length(seq2) + 1


  # set the score for match, mismatch and gap
  score_match <- score_match
  score_mismatch <- score_mismatch
  score_gap <- score_gap
  gap_char <- "-"

  F_matrix <- matrix(0, nrow = matrix_row, ncol = matrix_col)

  for (i in 2:matrix_row) {
    for (j in 2:matrix_col) {
      if (seq1[i - 1] == seq2[j - 1]) {
        score_d <- score_match
      } else {
        score_d <- score_mismatch
      }
      F_matrix[i, j] <- max(F_matrix[i - 1, j - 1] + score_d, F_matrix[i - 1, j] + score_gap, F_matrix[i, j - 1] + score_gap)
  }
  }

  print(F_matrix)



  alignment_seq1 <- ""
  alignment_seq2 <- ""

  i <- matrix_row
  j <- matrix_col

  while (i >= 2 && j >= 2) {
    if (F_matrix[i, j] == F_matrix[i - 1, j - 1] + score_match && seq1[i - 1] == seq2[j - 1]) {
      alignment_seq1 <- paste(seq1[i - 1], alignment_seq1, sep = "")
      alignment_seq2 <- paste(seq2[j - 1], alignment_seq2, sep = "")
      i <- i - 1
      j <- j - 1
    } else if (F_matrix[i, j] == F_matrix[i - 1, j - 1] + score_mismatch && seq1[i - 1] != seq2[j - 1]) {
      alignment_seq1 <- paste(seq1[i - 1], alignment_seq1, sep = "")
      alignment_seq2 <- paste(seq2[j - 1], alignment_seq2, sep = "")
      i <- i - 1
      j <- j - 1
    } else if (F_matrix[i, j] == F_matrix[i - 1, j] + score_gap) {
      alignment_seq1 <- paste(seq1[i - 1], alignment_seq1, sep = "")
      alignment_seq2 <- paste(gap_char, alignment_seq2, sep = "")
      i <- i - 1
    } else if (F_matrix[i, j] == F_matrix[i, j - 1] + score_gap) {
      alignment_seq1 <- paste(gap_char, alignment_seq1, sep = "")
      alignment_seq2 <- paste(seq2[j - 1], alignment_seq2, sep = "")
      j <- j - 1
    } else {
      break
    }
  }

  print(alignment_seq1)
  print(alignment_seq2)
}