# Load the ggplot2 library
library(ggplot2)

# Create a sample data frame
data <- data.frame(
    x = 1:10,
    y = rnorm(10)
)

# Create the plot
p <- ggplot(data, aes(x = x, y = y)) +
    geom_point() +
    labs(x = expression(hat(theta)), y = "Y-axis Label") +
    ggtitle("Plot with Theta^ Character on X-axis")

q <- ggplot(data, aes(x = x, y = y)) +
    geom_point() +
    labs(x = expression(hat(theta)), y = "Y-axis Label") +
    ggtitle("Plot with Theta^ Character on X-axis")

#plot size and resolution
ggsave("test.png", p, width = 10, height = 10, dpi = 300)
ggsave("test2.png", q, width = 10, height = 10, dpi = 300)