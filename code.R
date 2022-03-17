

# Libraries
library(magrittr)
library(dplyr)
library(ggplot2)
library(corrplot)

# 2014-2021 2k Ratings and Win Share + RPM for each player in each season
df <- read.csv("C:/Users/lahav/VSCode/Data Mining/Final Project/ESPN DATA/merged") %>% 
  dplyr::rename("2k_Rating" = .data$X2k.Rating, 'Age' = .data$birth.year) %>% 
  dplyr::mutate('Age' = .data$Year - .data$Age)

# 
df_stats <- read.csv('C:/Users/lahav/VSCode/Data Mining/Final Project/nba_rankings_2014-2020.csv')
#

# some sanity checks about the data
#######################################################

# correlation between Win-Share and 2k_rating
cor(df$`2k_Rating`, df$WIN_SHARE) # 0.57
# correlation between RPM and 2k_rating
cor(df$`2k_Rating`, df$RPM) # 0.52

# bar plot to show how many players in each year
ggplot(df, aes(fill = as.factor(Year), x = Year)) +
  geom_bar(position="dodge") + 
  scale_x_continuous(breaks = seq(2014, 2021, by=1)) +
  labs(title = "NBA players in each year", y = "number of players") +
  theme(legend.position="none") +
  geom_text(aes(label = ..count..), stat = "count", vjust = 1.5)


# box plot shows the player's ratings in each year
ggplot(df, aes(x = Year, y = `2k_Rating`, fill = as.factor(Year))) + 
  geom_boxplot() + 
  scale_x_continuous(breaks = seq(2014, 2021, by=1)) +
  labs(title = "2k Ratings boxplot per year", y = "2k Rating") +
  theme(legend.position="none")


hist((df$WIN_SHARE), breaks = 50, main = 'Histogram of WIN-SHARE', xlab='Win-Share')
hist(df$RPM, breaks = 50, main = 'Histogram of RPM', xlab='RPM')
hist((df$`2k_Rating`), breaks = 40, main = 'Histogram of players 2k_rating', xlab='2k rating')
#######################################################


# add new columns with the rating difference, win-share difference and RPM difference between each year
df %<>% dplyr::arrange(.data$Name, .data$Year)
diff_rating <- c(NA)
diff_WIN_SHARE <- c(NA)
diff_RPM <- c(NA)
for (row in 2:nrow(df)){
  if (df$Name[row] == df$Name[row-1]){
    diff_rating <- c(diff_rating, (df$`2k_Rating`[row] - df$`2k_Rating`[row-1]))
    diff_WIN_SHARE <- c(diff_WIN_SHARE, (df$WIN_SHARE[row] - df$WIN_SHARE[row-1]))
    diff_RPM <- c(diff_RPM, (df$RPM[row] - df$RPM[row-1]))
  } else{
    diff_rating <- c(diff_rating, NA)
    diff_WIN_SHARE <- c(diff_WIN_SHARE, NA)
    diff_RPM <- c(diff_RPM, NA)
  }
}

df %<>% dplyr::mutate("rating_change" = diff_rating,
                      "WIN_SHARE_change" = diff_WIN_SHARE,
                      "RPM_change" = diff_RPM)

# average rating change for each year 
ggplot(df, aes(x = Year, y = abs(rating_change), fill = as.factor(Year))) +
  geom_bar(position = "dodge", stat = "summary", fun = "mean") +
  labs(title = "The average 2k rating change for each year", y = "average rating change") +
  scale_x_continuous(breaks = seq(2014,2021,by=1)) +
  theme(legend.position = "none")


# how well they predict- WIN-SHARE change vs. rating change
ggplot(df, aes(x = rating_change, 
               y = WIN_SHARE_change, 
               col = dplyr::case_when((rating_change > 0 & WIN_SHARE_change > 0) ~ 'red',
                                      (rating_change > 0 & WIN_SHARE_change < 0) ~ 'blue',
                                      (rating_change < 0 & WIN_SHARE_change > 0) ~ 'blue',
                                      (rating_change < 0 & WIN_SHARE_change < 0) ~ 'red'))) + 
  geom_point(size=3.5) +
  labs(title = "Win-Share change vs. 2k rating change", x = "rating change", y = "Win-Share change") +
  geom_hline(yintercept = 0, col="black") +
  geom_vline(xintercept = 0, col="black") +
  theme(legend.position = "none")

# ages vs. rating change
top_100_pos_rating_change <- df %>% dplyr::filter(.data$rating_change > 0) %>% 
  dplyr::arrange(desc(.data$rating_change)) %>%
  head(100)
top_100_neg_rating_change <- df %>% dplyr::filter(.data$rating_change < 0) %>% 
  dplyr::arrange(.data$rating_change) %>%
  head(100)

x1 <- mean(top_100_pos_rating_change$Age)
x2 <- mean(top_100_neg_rating_change$Age)

b <- barplot(c(x1, x2), beside = TRUE, ylab = 'Age',
             main = 'Average Age of top 2k rating change',
             ylim = c(19, 32), col = c("lightgreen", "lightblue"), xpd=FALSE)
axis(side=1,at=b,labels=c("Top 100 positive rating change", "Top 100 negative rating change"))
box(bty="l")

#####

# regression line between WIN-SHARE~2k_Rating and RPM~2k_Rating
# rating_vs_WS <- lm(df$`2k_Rating` ~ df$WIN_SHARE + df$RPM)
# 
# summary(rating_vs_WS)
# 
# ggplot(df, aes(y = `2k_Rating`, x = WIN_SHARE)) + 
#   geom_point(aes(col=`2k_Rating`)) + geom_smooth(method="lm", se=FALSE) +
#   labs(title="",subtitle = "") #+ 
#   xlim(c(-6,10)) + ylim(c(60,100))

# out of the usa
out_USA <- df %>% dplyr::filter(.data$Country != 'USA')
print(paste0("The fraction of players not from the USA ", round(nrow(out_USA)/nrow(df),3)))
frac_top_change_out_US <- nrow((top_100_pos_rating_change %>% dplyr::filter(.data$Country != 'USA')))/nrow(top_100_pos_rating_change)
print(paste0("The fraction of players not from the USA in the top 100 players with rating change ", round(frac_top_change_out_US,3)))

# correlation between stats and 2k_rating + win share
df_stats %<>% dplyr::mutate('SEASON' = as.integer(paste0('20', substr(.data$SEASON, 6, 7)))) %>% 
  dplyr::rename('Year' = .data$SEASON, 'Name' = .data$PLAYER) 

merged <- dplyr::inner_join(df_stats, df, by = c('Name', 'Year')) %>% 
  dplyr::select(-.data$rankings, -.data$AGE)


cor_stats <- cor(merged[,c(8:26, 31:33)])
corrplot(cor_stats, order='hclust', tl.cex = 0.7, mar=c(0,0,1,0))

