# Age (thousands of vears) Depth (m)
# 12.05 1.85
# 17.85 2.2
# 24.11 3
# 43.88 6.2
# 50.21 6.65
# 55.45 7.2
# 58.96 7.45
# 64.09 8
# 73.91 8.7
# 79.25 9.8
# 90.95 10.55
# 96.21 11.15
# 103.29 11.8
# 110.79 12.55
# 122.56 13.45
# 123.82 13.75
# 125.19 14.05
# 129.84 14.45
# 142.28 16.75
# 152.58 17.5
# 161.34 18.5

library(ggplot2)
library(tibble)

# generate dataframe of vectors age and depth using tidyverse's tibble function

age = c(12.05, 17.85, 24.11, 43.88, 50.21, 55.45, 58.96, 64.09, 73.91, 79.25, 90.95, 96.21, 103.29, 110.79, 122.56, 123.82, 125.19, 129.84, 142.28, 152.58, 161.34)
depth = c(1.85, 2.2, 3, 6.2, 6.65, 7.2, 7.45, 8, 8.7, 9.8, 10.55, 11.15, 11.8, 12.55, 13.45, 13.75, 14.05, 14.45, 16.75, 17.5, 18.5)

df = tibble(age, depth)

# plot age vs depth

model = lm(depth ~ age, data = df)

print(summary(model))

# print the formula for the model
print(model)

# plot age vs depth with model "model" with print black and white style and print the model and the formula for the model and r^2 value with 4:3 aspect ratio

plot <- ggplot(df, aes(x = age, y = depth)) + geom_point() + labs(x = "Age (thousands of years)", y = "Depth (m)", title = "Age vs Depth") + geom_line(aes(x = age, y = predict(model, df)), color = "black", size = 1) + theme_bw() + geom_text(aes(x = 50, y = 10, label = paste("y = ", round(model$coefficients[1], 2), " + ", round(model$coefficients[2], 2), "x", ", R^2 = ", round(summary(model)$r.squared, 2))), size = 5) + theme(plot.title = element_text(hjust = 0.5)) + theme(aspect.ratio = 3/4)

print(plot)

# save plot as png file

ggsave("plot.png", plot = plot, width = 10, height = 7.5, units = "in", dpi = 300)

# save plot as pdf file

ggsave("plot.pdf", plot = plot, width = 10, height = 7.5, units = "in", dpi = 300)

