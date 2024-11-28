# Last inn nødvendig bibliotek
library(jsonlite)
library(dplyr)
library(ggplot2)
library(lubridate)
library(tidyr)

# Les JSON-filen
# Erstatt 'path/to/your/file.json' med den faktiske filbanen til din JSON-fil
data <- fromJSON('Processed_Google_ratings.json', simplifyVector = TRUE)

# Konverter data til en tibble (dataframe)
data <- as_tibble(data)

# Vis de første radene i datasettet
head(data)

# Vis strukturen til datasettet
str(data)

# Hvis 'categories' er en liste-kolonne, kan du konvertere den til separate kolonner
data <- data %>%
  mutate(across(where(is.list), as.data.frame),
         Dato = ymd(substr(Dato, 1, 10))) %>% 
        unnest_wider(categories) %>% 
  rename(
    Positiv = `Positiv tilbakemelding`,
    Produkter = `Dårlige produkter`,
    Kundeservice = `Dårlig kundeservice/opplevelse`,
    Ventetid = `Lang kø/ventetid`,
    Renhold = `Dårlig renhold`,
    Kommentar = `Ingen kommentar`,
    Annet = `Annet`,
    Rating= `★`
  ) %>% 
  filter(Dato > '2019-12-31',
         Avd != "16 EV") 

colnames(data)


# Regresjon ---------------------------------------------------------------

# Funksjon for å utføre regresjon per avdeling
run_regression <- function(department_data) {
  # Kontroller datastruktur
  if (!"Rating" %in% colnames(department_data)) {
    stop("Kolonnen 'Rating' finnes ikke i department_data")
  }
  
  # Bygg lineær modell
  model <- lm(Rating ~ Positiv + Produkter + Kundeservice + Ventetid + Renhold + Kommentar + Annet,
              data = department_data)
  
  # Hent resultater og filtrer basert på p-verdi
  tidy(model) %>%
    mutate(Significant = p.value < 0.05) %>%
    arrange(term) %>%
    select(term, estimate, p.value, Significant)
}

# Bruk regresjonsfunksjonen for hver avdeling
regression_results <- data %>%
  group_by(Avd) %>%
  group_map(~ run_regression(.x), .keep = TRUE) %>%
  setNames(unique(data$Avd))

# Kombiner resultatene i en matrise og sortér etter avdeling
final_results <- do.call(rbind, lapply(names(regression_results), function(name) {
  cbind(Avdeling = name, regression_results[[name]])
}))

# Konverter til data frame
final_results <- as.data.frame(final_results)

# Sorter resultatene etter avdeling
final_results <- final_results[order(final_results$Avdeling), ]

# Vis resultatene
print(final_results)


# Visualisering Regresjon -------------------------------------------------

# Filtrer kun signifikante resultater
significant_effects <- final_results %>%
  filter(Significant == TRUE, 
         term != "(Intercept)",
         term != "Kommentar",
         term != "Positiv"
         ) %>%
  mutate(estimate_abs = abs(as.numeric(estimate)))

# Lag et heatmap
ggplot(significant_effects, aes(x = term, y = Avdeling, fill = estimate_abs)) +
  geom_tile(color = "white") +
  scale_fill_gradient(low = "blue", high = "red", name = "Absolutt effekt") +
  labs(
    title = "Signifikante variabler per avdeling",
    x = "Variabel",
    y = "Avdeling"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1, size = 10),
    axis.text.y = element_text(size = 10),
    plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
    legend.position = "right",
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 10)
  )





# Top_3 -------------------------------------------------------------------

# Beregn topp 3 svakheter per avdeling
top_weaknesses <- final_results %>%
  filter(Significant == TRUE & estimate < 0 & term != "(Intercept)",
         term != "Kommentar",
         term != "Positiv"
  ) %>% # Filtrer signifikante negative verdier
  group_by(Avdeling) %>%
  arrange(estimate) %>% # Sorter etter estimate (stigende rekkefølge, dvs. mest negativ først)
  slice_head(n = 3) %>% # Velg de 3 svakeste attributtene per avdeling
  mutate(
    Forklaringskraft = abs(estimate) / sum(abs(estimate)) # Beregn forklaringskraft for hver svakhet
  )

# Vis resultatene
print(top_weaknesses)



# Visualisering av topp dårligste -----------------------------------------


# Lag en visualisering for topp 3 svakeste attributter per avdeling
ggplot(top_weaknesses, aes(x = term, y = Avdeling, fill = estimate)) +
  geom_tile(color = "white") +
  scale_fill_gradient2(low = "red", mid = "white", high = "blue", midpoint = 0, name = "Estimate") +
  labs(
    title = "Topp 3 svakeste attributter per avdeling",
    x = "Attributter",
    y = "Avdeling"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    axis.text.y = element_text(size = 10),
    plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
    legend.position = "right",
    legend.title = element_text(size = 12),
    legend.text = element_text(size = 10)
  )

# Filter data -------------------------------------------------------------

data <- data %>% 
  filter(
    `Ingen kommentar`==0,
    `★`<5,
    Dato > '2000-12-31',
    Avd != "16 EV") %>% 
  rename(`Dårlig kundeservice` = `Dårlig kundeservice/opplevelse`)


# Annet_justert -----------------------------------------------------------

data <- data %>%
  mutate(Annet = case_when(
    `Positiv tilbakemelding` == 0 &
      `Dyre produkter` == 0 &
      `Dårlige produkter` == 0 &
      `Dårlig kundeservice` == 0 &
      `Dårlig renhold` == 0 &
      `Lang kø/ventetid` == 0 &
      `Ingen kommentar` == 0 &
      Annet == 0 ~ 1,
    TRUE ~ Annet
  ))



# Antall tilbakemeldinger -------------------------------------------------



# Define negative attributes
negative_attributes <- c("Dyre produkter", "Dårlige produkter", "Dårlig kundeservice", 
                         "Lang kø/ventetid", "Dårlig renhold")

# Calculate the top 3 negative attributes for each department
top_negative_attributes <- data %>%
  select(Avd, all_of(negative_attributes)) %>%
  pivot_longer(cols = -Avd, names_to = "Attributt", values_to = "Verdi") %>%
  group_by(Avd, Attributt) %>%
  summarise(Sum = sum(Verdi), .groups = "drop") %>%
  arrange(Avd, desc(Sum)) %>%
  group_by(Avd) %>%
  slice_max(Sum, n = 3)

# Plot the results
ggplot(top_negative_attributes, aes(x = reorder(Avd, -Sum), y = Sum, fill = Attributt)) +
  geom_col(position = "dodge") +
  labs(title = "Top 3 Negative Attributes per Department",
       x = "Department",
       y = "Count") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_fill_brewer(palette = "Set1")


# Attributer per område ---------------------------------------------------


library(dplyr)
library(tidyr)
library(ggplot2)

# Define negative attributes
negative_attributes <- c("Dyre produkter", "Dårlige produkter", "Dårlig kundeservice", 
                         "Lang kø/ventetid", "Dårlig renhold")

# Calculate the top 3 negative attributes for each department
top_negative_attributes <- data %>%
  select(Avd, all_of(negative_attributes)) %>%
  pivot_longer(cols = -Avd, names_to = "Attributt", values_to = "Verdi") %>%
  group_by(Avd, Attributt) %>%
  summarise(Sum = sum(Verdi), .groups = "drop") %>%
  arrange(Avd, desc(Sum)) %>%
  group_by(Avd) %>%
  slice_max(Sum, n = 3)

# Plot the results
ggplot(top_negative_attributes, aes(x = reorder(Avd, -Sum), y = Sum, fill = Attributt)) +
  geom_col(position = "dodge") +
  labs(title = "Top 3 Negative Attributes per Department",
       x = "Department",
       y = "Count") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_fill_brewer(palette = "Set1")


library(dplyr)
library(tidyr)

# Define department codes for each area
bergen_codes <- c("11", "12", "13", "22", "24", "26", "31", "36", "40")
oslo_codes <- c("17", "19", "20", "21", "23", "25", "27", "28", "29", "32")

# Function to determine area based on department code
get_area <- function(avd) {
  if (substr(avd, 1, 2) %in% bergen_codes) {
    return("Bergen")
  } else if (substr(avd, 1, 2) %in% oslo_codes) {
    return("Oslo")
  } else {
    return("Rest")
  }
}

# Add area column to the data
data <- data %>%
  mutate(Area = sapply(Avd, get_area))

# Define negative attributes
negative_attributes <- c("Dyre produkter", "Dårlige produkter", 
                         "Dårlig kundeservice", 
                         "Lang kø/ventetid", "Dårlig renhold")

# Function to get top 3 negative attributes for each area
get_top_attributes <- function(data) {
  data %>%
    select(Avd, all_of(negative_attributes)) %>%
    pivot_longer(cols = -Avd, names_to = "Attributt", values_to = "Verdi") %>%
    group_by(Avd, Attributt) %>%
    summarise(Sum = sum(Verdi), .groups = 'drop') %>%
    arrange(desc(Sum)) %>%
    group_by(Avd) %>%
    slice_max(Sum, n = 3)
}

# Generate reports for each area
bergen_report <- data %>% filter(Area == "Bergen") %>% get_top_attributes()
oslo_report <- data %>% filter(Area == "Oslo") %>% get_top_attributes()
rest_report <- data %>% filter(Area == "Rest") %>% get_top_attributes()

# Print reports
print("Bergen Report:")
print(bergen_report)

print("Oslo Report:")
print(oslo_report)

print("Rest Report:")
print(rest_report)


# graf* -------------------------------------------------------------------

library(dplyr)
library(tidyr)
library(ggplot2)

# Define department codes for each area
bergen_codes <- c("11", "12", "13", "22", "24", "26", "31", "36", "40")
oslo_codes <- c("17", "19", "20", "21", "23", "25", "27", "28", "29", "32")

# Function to determine area based on department code
get_area <- function(avd) {
  if (substr(avd, 1, 2) %in% bergen_codes) {
    return("Bergen")
  } else if (substr(avd, 1, 2) %in% oslo_codes) {
    return("Oslo")
  } else {
    return("Rest")
  }
}

# Add area column to the data
data <- data %>%
  mutate(Area = sapply(Avd, get_area))

# Define negative attributes
negative_attributes <- c("Dyre produkter", "Dårlige produkter", 
                         "Dårlig kundeservice", 
                         "Lang kø/ventetid", "Dårlig renhold")

# Function to get top 3 negative attributes for each department
get_top_attributes <- function(data) {
  data %>%
    select(Avd, all_of(negative_attributes)) %>%
    pivot_longer(cols = -Avd, names_to = "Attributt", values_to = "Verdi") %>%
    group_by(Avd, Attributt) %>%
    summarise(Sum = sum(Verdi), .groups = 'drop') %>%
    arrange(desc(Sum)) %>%
    group_by(Avd) %>%
    slice_max(Sum, n = 3)
}

# Generate reports for each area
bergen_report <- data %>% filter(Area == "Bergen") %>% get_top_attributes()
oslo_report <- data %>% filter(Area == "Oslo") %>% get_top_attributes()
rest_report <- data %>% filter(Area == "Rest") %>% get_top_attributes()

# Plot function for each area
plot_area <- function(report, area_name) {
  ggplot(report, aes(x = Avd, y = Sum, fill = Attributt)) +
    geom_col(position = position_dodge()) +
    labs(title = paste("Top 3 Negative Attributes per Department in", area_name),
         x = "Department",
         y = "Count") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    scale_fill_brewer(palette = "Set1")
}

# Plot each area
plot_area(bergen_report, "Bergen")
plot_area(oslo_report, "Oslo")
plot_area(rest_report, "Rest")


# justert -----------------------------------------------------------------


library(dplyr)
library(tidyr)
library(ggplot2)

# Define department codes for each area
bergen_codes <- c("11", "12", "13", "22", "24", "26", "31", "36", "40")
oslo_codes <- c("17", "19", "20", "21", "23", "25", "27", "28", "29", "32")

# Function to determine area based on department code
get_area <- function(avd) {
  if (substr(avd, 1, 2) %in% bergen_codes) {
    return("Bergen")
  } else if (substr(avd, 1, 2) %in% oslo_codes) {
    return("Oslo")
  } else {
    return("Rest")
  }
}

# Add area column to the data
data <- data %>%
  mutate(Area = sapply(Avd, get_area))

# Define negative attributes
negative_attributes <- c("Dyre produkter", "Dårlige produkter", 
                         "Dårlig kundeservice", 
                         "Lang kø/ventetid", "Dårlig renhold")

# Oppdatert funksjon for å få topp 3 negative attributter og normalisere dem
get_top_attributes <- function(data) {
  data %>%
    select(Avd, all_of(negative_attributes)) %>%
    pivot_longer(cols = -Avd, names_to = "Attributt", values_to = "Verdi") %>%
    group_by(Avd, Attributt) %>%
    summarise(Sum = sum(Verdi), .groups = 'drop') %>%
    group_by(Avd) %>%
    mutate(Normalized_Sum = rescale(Sum)) %>%
    slice_max(Normalized_Sum, n = 3) %>%
    ungroup()
}

# Generate reports for each area
bergen_report <- data %>% filter(Area == "Bergen",
                                 Avd != "40 FLOTT") %>% get_top_attributes()
oslo_report <- data %>% filter(Area == "Oslo") %>% get_top_attributes()
rest_report <- data %>% filter(Area == "Rest") %>% get_top_attributes()

# Oppdatert plottfunksjon for hvert område med normaliserte data
plot_area <- function(report, area_name) {
  report <- report %>%
    mutate(SortOrder = as.numeric(gsub("\\D", "", Avd))) %>% # Ekstraher tall fra avdelingsnavn
    arrange(SortOrder) # Sorter etter de ekstraherte tallene
  
  ggplot(report, aes(x = reorder(Avd, SortOrder), y = Normalized_Sum, fill = Attributt)) +
    geom_col(position = position_dodge(width = 0.9), color = "white", size = 0.2) +
    labs(
      title = paste("Topp 3 negative attributter i", area_name),
      subtitle = "Kundetilbakemeldinger (normaliserte data)",
      x = "Avdeling",
      y = NULL,
      fill = "Attributt"
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(size = 10, face = "bold"),
      axis.text.y = element_text(size = 10, face = "bold"),
      axis.title.x = element_text(size = 12, face = "bold"),
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      plot.subtitle = element_text(hjust = 0.5, size = 10),
      legend.position = "bottom",
      legend.title = element_text(size = 10),
      legend.text = element_text(size = 9),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank()
    ) +
    scale_fill_manual(values = c(
      "Dyre produkter" = "black", # Sterk blå
      "Dårlige produkter" = "#2a7bdc", # Lysere blå
      "Dårlig kundeservice" = "#88ccee", # Klar cyanblå
      "Lang kø/ventetid" = "grey", # Markant oransje
      "Dårlig renhold" = "darkblue"  # Sterk rød-oransje
    )) +
    coord_flip() +
    scale_y_continuous(expand = expansion(mult = c(0, 0.1)))
}


# Plot each area
plot_area(bergen_report, "Bergen")
plot_area(oslo_report, "Oslo")
plot_area(rest_report, "Rest")



# juster for dyre produkter -----------------------------------------------



library(dplyr)
library(tidyr)
library(ggplot2)

# Define department codes for each area
bergen_codes <- c("11", "12", "13", "22", "24", "26", "31", "36", "40")
oslo_codes <- c("17", "19", "20", "21", "23", "25", "27", "28", "29", "32")

# Function to determine area based on department code
get_area <- function(avd) {
  if (substr(avd, 1, 2) %in% bergen_codes) {
    return("Bergen")
  } else if (substr(avd, 1, 2) %in% oslo_codes) {
    return("Oslo")
  } else {
    return("Rest")
  }
}

# Add area column to the data
data <- data %>%
  mutate(Area = sapply(Avd, get_area))

# Define negative attributes
negative_attributes <- c( "Dårlige produkter", 
                         "Dårlig kundeservice", 
                         "Lang kø/ventetid", "Dårlig renhold")

# Oppdatert funksjon for å få topp 3 negative attributter og normalisere dem
get_top_attributes <- function(data) {
  data %>%
    select(Avd, all_of(negative_attributes)) %>%
    pivot_longer(cols = -Avd, names_to = "Attributt", values_to = "Verdi") %>%
    group_by(Avd, Attributt) %>%
    summarise(Sum = sum(Verdi), .groups = 'drop') %>%
    group_by(Avd) %>%
    mutate(Normalized_Sum = rescale(Sum)) %>%
    slice_max(Normalized_Sum, n = 3) %>%
    ungroup()
}

# Generate reports for each area
bergen_report <- data %>% filter(Area == "Bergen",
                                 Avd != "40 FLOTT") %>% get_top_attributes()
oslo_report <- data %>% filter(Area == "Oslo") %>% get_top_attributes()
rest_report <- data %>% filter(Area == "Rest") %>% get_top_attributes()

# Oppdatert plottfunksjon for hvert område med normaliserte data
plot_area <- function(report, area_name) {
  report <- report %>%
    mutate(SortOrder = as.numeric(gsub("\\D", "", Avd))) %>% # Ekstraher tall fra avdelingsnavn
    arrange(SortOrder) # Sorter etter de ekstraherte tallene
  
  ggplot(report, aes(x = reorder(Avd, SortOrder), y = Normalized_Sum, fill = Attributt)) +
    geom_col(position = position_dodge(width = 0.9), color = "white", size = 0.2) +
    labs(
      title = paste("Topp 3 negative attributter i", area_name),
      subtitle = "Kundetilbakemeldinger (normaliserte data)",
      x = "Avdeling",
      y = NULL,
      fill = "Attributt"
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(size = 10, face = "bold"),
      axis.text.y = element_text(size = 10, face = "bold"),
      axis.title.x = element_text(size = 12, face = "bold"),
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      plot.subtitle = element_text(hjust = 0.5, size = 10),
      legend.position = "bottom",
      legend.title = element_text(size = 10),
      legend.text = element_text(size = 9),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank()
    ) +
    scale_fill_manual(values = c(
      "Dyre produkter" = "black", # Sterk blå
      "Dårlige produkter" = "#2a7bdc", # Lysere blå
      "Dårlig kundeservice" = "#88ccee", # Klar cyanblå
      "Lang kø/ventetid" = "grey", # Markant oransje
      "Dårlig renhold" = "darkblue"  # Sterk rød-oransje
    )) +
    coord_flip() +
    scale_y_continuous(expand = expansion(mult = c(0, 0.1)))
}


# Plot each area
plot_area(bergen_report, "Bergen")
plot_area(oslo_report, "Oslo")
plot_area(rest_report, "Rest")


