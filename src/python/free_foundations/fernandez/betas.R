# Fernández stage one: quarterly factor regressions with a high-breakdown MM estimator.
# Usage: Rscript betas.R data.csv out.csv terms [indices.csv] [cores]
#   data.csv:    quarter, ticker, excess and one column per comma-separated term.
#   indices.csv: replicate, position, quarter; each replicate lists resampled quarters.
# Every fit resets the seed, so estimates do not depend on firm order or cohort.
args <- commandArgs(trailingOnly = TRUE)
data <- read.csv(args[1], check.names = FALSE)
terms <- strsplit(args[3], ",", fixed = TRUE)[[1]]
indices <- if (length(args) >= 4 && nzchar(args[4])) read.csv(args[4]) else NULL
cores <- if (length(args) >= 5) as.integer(args[5]) else 1L
formula <- stats::reformulate(terms, response = "excess")
control <- robustbase::lmrob.control()
version <- as.character(utils::packageVersion("robustbase"))

# Fits that do not converge with the defaults are refitted once with larger iteration
# limits; the `retried` column records this.
retry <- robustbase::lmrob.control(max.it = 500, k.max = 2000, maxit.scale = 2000)

fit_firm <- function(firm, replicate) {
  warnings <- 0L
  attempt <- function(control) {
    set.seed(42)
    withCallingHandlers(
      tryCatch(robustbase::lmrob(formula, data = firm, method = "MM", control = control),
               error = function(e) NULL),
      warning = function(w) {
        warnings <<- warnings + 1L
        invokeRestart("muffleWarning")
      }
    )
  }
  fit <- attempt(control)
  retried <- is.null(fit) || !isTRUE(fit$converged)
  if (retried) fit <- attempt(retry)
  names <- c("(Intercept)", terms)
  estimates <- if (is.null(fit)) rep(NA_real_, length(names)) else unname(coef(fit)[names])
  data.frame(
    replicate = replicate, ticker = firm$ticker[1], term = c("intercept", terms),
    estimate = estimates, converged = !is.null(fit) && isTRUE(fit$converged),
    warnings = warnings, retried = retried, observations = nrow(firm),
    package_version = version
  )
}

fit_replicate <- function(replicate) {
  sample <- data
  if (!is.null(indices)) {
    order <- indices[indices$replicate == replicate, ]
    order <- order[order(order$position), ]
    sample <- do.call(rbind, lapply(split(data, data$ticker), function(firm) {
      firm[match(order$quarter, firm$quarter), ]
    }))
  }
  do.call(rbind, lapply(split(sample, sample$ticker), fit_firm, replicate = replicate))
}

replicates <- if (is.null(indices)) 0L else sort(unique(indices$replicate))
rows <- parallel::mclapply(replicates, fit_replicate, mc.cores = cores)
write.csv(do.call(rbind, rows), args[2], row.names = FALSE)
runtime <- data.frame(
  name = c("r_version", "robustbase_version", "method", "psi", "tuning_psi", "bb",
           "nResample", "seed", "retry"),
  value = c(R.version.string, version, "MM", control$psi,
            paste(format(control$tuning.psi), collapse = ";"), control$bb,
            control$nResample, "42 before every firm fit",
            "if not converged: max.it=500, k.max=2000, maxit.scale=2000")
)
write.csv(runtime, sub("\\.csv$", "-runtime.csv", args[2]), row.names = FALSE)
