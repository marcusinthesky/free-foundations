# Fernández stage one: quarterly factor regressions with a high-breakdown MM estimator.
# Usage: Rscript betas.R data.csv out.csv terms [indices.csv] [cores] [backend]
#   data.csv:    quarter, ticker, excess and one column per comma-separated term.
#   indices.csv: replicate, position, quarter; each replicate lists resampled quarters.
# Every fit resets the seed, so estimates do not depend on firm order or cohort.
args <- commandArgs(trailingOnly = TRUE)
data <- read.csv(args[1], check.names = FALSE)
terms <- strsplit(args[3], ",", fixed = TRUE)[[1]]
indices <- if (length(args) >= 4 && nzchar(args[4])) read.csv(args[4]) else NULL
cores <- if (length(args) >= 5) as.integer(args[5]) else 1L
backend <- if (length(args) >= 6) args[6] else "robustbase"
if (!backend %in% c("robustbase", "robust")) stop("Unknown MM backend: ", backend)
if (!requireNamespace(backend, quietly = TRUE)) {
  stop("Run inside the updated devenv shell: missing R package ", backend)
}
formula <- stats::reformulate(terms, response = "excess")
version <- as.character(utils::packageVersion(backend))
if (backend == "robustbase") {
  # Keep the primary estimator and retry controls identical to the retained benchmark.
  control <- robustbase::lmrob.control()
  retry <- robustbase::lmrob.control(max.it = 500, k.max = 2000, maxit.scale = 2000)
  retry_label <- "if not converged: max.it=500, k.max=2000, maxit.scale=2000"
  completion_rule <- "lmrob converged flag and finite coefficients"
} else {
  control <- robust::lmRob.control(estim = "Final", final.alg = "MM", seed = 42,
                                  efficiency = 0.90, weight = c("Optimal", "Optimal"),
                                  trace = FALSE)
  retry <- robust::lmRob.control(estim = "Final", final.alg = "MM", seed = 42,
                                efficiency = 0.90, weight = c("Optimal", "Optimal"),
                                trace = FALSE, mxr = 500, mxf = 500, mxs = 500)
  retry_label <- "if incomplete: mxr=500, mxf=500, mxs=500"
  # lmRob has no lmrob-style convergence flag; retain its documented iteration counts.
  completion_rule <- paste("finite full-rank final-MM fit; refinement and final iterations",
                           "below limits; no numerical/convergence warnings")
}

complete <- function(fit, control, messages) {
  if (is.null(fit) || any(!is.finite(coef(fit)))) return(FALSE)
  if (backend == "robustbase") return(isTRUE(fit$converged))
  final <- identical(tolower(fit$est), "final")
  rank <- isTRUE(fit$rank == length(coef(fit)))
  iterations <- c(fit$iter.refinement, fit$iter.final.coef)
  below_limits <- length(iterations) == 2 && all(is.finite(iterations)) &&
    all(iterations < c(control$mxr, control$mxf))
  adverse <- any(grepl("converg|iteration|singular|rank|failed|failure|NaN|infinite",
                       messages, ignore.case = TRUE))
  final && rank && below_limits && !adverse
}

fit_firm <- function(firm, replicate) {
  warnings <- character()
  errors <- character()
  attempt <- function(settings) {
    set.seed(42)
    withCallingHandlers(
      tryCatch(
        if (backend == "robustbase") {
          robustbase::lmrob(formula, data = firm, method = "MM", control = settings)
        } else {
          robust::lmRob(formula, data = firm, control = settings)
        },
        error = function(e) {
          errors <<- c(errors, conditionMessage(e))
          NULL
        }
      ),
      warning = function(w) {
        warnings <<- c(warnings, conditionMessage(w))
        invokeRestart("muffleWarning")
      }
    )
  }
  fit <- attempt(control)
  retried <- !complete(fit, control, warnings)
  settings <- control
  final_warnings <- warnings
  if (retried) {
    settings <- retry
    prior_warnings <- length(warnings)
    fit <- attempt(retry)
    final_warnings <- warnings[seq_along(warnings) > prior_warnings]
  }
  names <- c("(Intercept)", terms)
  estimates <- if (is.null(fit)) rep(NA_real_, length(names)) else unname(coef(fit)[names])
  data.frame(
    replicate = replicate, ticker = firm$ticker[1], term = c("intercept", terms),
    estimate = estimates, converged = complete(fit, settings, final_warnings),
    warnings = length(warnings), retried = retried, observations = nrow(firm),
    package_version = version, backend = backend,
    warning_messages = paste(unique(warnings), collapse = " | "),
    error_messages = paste(unique(errors), collapse = " | "),
    iteration_refinement = if (is.null(fit$iter.refinement)) NA_real_ else fit$iter.refinement,
    iteration_final = if (is.null(fit$iter.final.coef)) NA_real_ else fit$iter.final.coef,
    completion_rule = completion_rule
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
serialize <- function(value) paste(format(value), collapse = ";")
runtime <- c(
  r_version = R.version.string, backend = backend, package_version = version,
  method = "MM", seed = "42 before every firm fit", retry = retry_label,
  completion_rule = completion_rule,
  stats::setNames(vapply(control, serialize, character(1)), paste0("control.", names(control))),
  stats::setNames(vapply(retry, serialize, character(1)), paste0("retry_control.", names(retry)))
)
if (backend == "robustbase") {
  # Existing runtime keys remain available to consumers of the primary benchmark.
  runtime <- c(runtime, robustbase_version = version, psi = control$psi,
               tuning_psi = serialize(control$tuning.psi), bb = control$bb,
               nResample = control$nResample)
} else runtime <- c(runtime, robust_version = version)
write.csv(data.frame(name = names(runtime), value = unname(runtime)),
          sub("\\.csv$", "-runtime.csv", args[2]), row.names = FALSE)
