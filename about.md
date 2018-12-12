---
layout: page
title: Predicting the Success of a Theatrical Production
permalink: /MLproject/
---
###### Created by: Harper Pack, Brandon Harris and Michael Cantu

###### ABSTRACT


<p> 
We sought to predict the success of a show at one of Chicago’s premier theater companies (hereafter the “Theater”; actual name withheld at the request of the institution).  Our task is an important one insofar as its successful completion could provide material support to the Theater, which is a significant thread in the cultural fabric of Chicago.  It is incumbent upon such cultural institutions to ensure they remain both financially viable and socially relevant.  We believe the ability to anticipate the success of a show prior to investing in its production would help the Theater in its pursuit of these goals.
</p>

<p> 
The Theater shared with us data listing performance dates and tickets sold, and through research and perseverance we developed features for season, daypart, genre, venue, minimum ticket price, production length, national origin of the production, recurring productions, and family-oriented productions.  We chose percentage of seats sold as our classification variable, and thus we favored learners that allowed classification using continuous variables.  We experimented with k-nearest neighbor, linear regression, additive regression, random forests, M5’, and neural networks.  Random forests and M5’ produced the best results, with R2 values of 0.59 and 0.58 and root-mean-squared errors of .131 and .132, respectively.  These classifiers suggested that “venue” was the most important feature, but neither are well-suited for feature selection. Looking ahead to future work, we believe better results will require more data.  In particular, we think more ticket pricing and marketing/advertising data would be especially valuable.
</p>

 <img src='../img/biggergraph.jpg' width="500" height="600"> 
 <em>Figure 1 above illustrates our M5' tree. 
 <b>Please right click image to open in new tab to zoom in.
<!--  <img class="picbig" src='../img/biggergraph.jpg' alt="big"> -->
<br>
<br>
###### Detailed Final Report
<p>
Our dataset comprised 5,915 individual performances from 162 unique shows across the
Theater’s three venues, covering the twelve seasons from 2006 to 2018. The initial data we
received from the Theater contained just two features: performance date and seats sold,
spread across a dozen files (one for each season). We aggregated these into a single dataset
and researched each of the shows to enrich our data with additional features.
Relying on data available on the Theater’s website, archived webpages from Chicago
theater websites, and Wikipedia, we were able to create features describing a production’s
showtime, run length, season, weekday, recurrence (whether that show had previously been
performed at the Theater), family/youth-orientation, national origin, minimum ticket price,
genre, and whether it was a Shakespeare play. We did not divide the data into training and test
sets, instead opting for ten-fold-cross-validation to evaluate the performance of our classifiers.
As our final step in data processing, we normalized seats sold as percentage of seats
filled to retain comparability between the differently-sized venues. We considered using
categories instead of continuously-valued percentages, but the results of the categorical
analysis we later performed had limited value because the standard deviation of the data was
low. The bins had to be narrow to provide significant value to the Theater, and we were unable
to achieve good accuracy in these instances. We also explored a binary classifier to predict
whether the Theater would fill to more or less than 90% capacity, but these results were
similarly underwhelming.
With our dataset complete, we began experimenting with learners which would allow
for classification with continuous values. We first experimented with ZeroR because our data
had low variance. ZeroR performed well: our mean absolute error was 0.133 and our root
mean squared error (RMS) was 0.162. Given that mean absolute error equates to percentage
points, we concluded that ZeroR had non-negligible predictive power on our dataset.
We turned next to linear regression. Beyond predictive validity, we expected that linear
regression might qualify the importance of the features in our dataset. We further expected
linear regression to be an extension of our reasonable ZeroR results, as ZeroR is linear
regression with the slope locked at 0. After achieving R 2 of only 0.31 and a 0.154 RMS, we
switched to Additive Regression. We hoped that an ensemble method might offer better
performance while retaining interpretability, but its 0.37 R 2 and 0.151 RMS were not material
improvements. Yet these experiments were not without value, as our classifiers were able
offer some insight into feature significance. The regressions saw venue and genre as the most
salient features, but the weightings it assigned to each were not much greater than those it
assigned to the other features.
We then moved to a k-nearest-neighbor learner, reasoning that the best measure of
success for a given show may instead be how other shows with similar features had performed.
We found an R 2 of nearly 0.5 and RMS of 0.141. Varying our “k” proved immaterial, which we
suspect to be because the average production had more than 48 shows. With so many shows in
a similar space, increasing the “neighbors” considered by the model effected only minor
changes.
We next experimented with the random forest and M5’ learners. We thought that
these might fare better than our regressors because they combined regression with the

categorical utility of decision trees. Random forest and M5’ capitalized on this promise,
delivering R 2 of 0.59 and 0.58 and RMS of 0.131 and 0.132, respectively. We explored different
bag sizes for our random forest learner, but these adjustments proved ineffective, possibly due
to the significant similarity of data for different performances of the same show, which almost
any bag would contain at least one of each. The parity between random forest and M5’
performance came as a surprise, as we thought that M5’ would struggle with the small size of
our dataset. We presumed random forest would not have such struggles due to its ability to
artificially create datasets through bagging. These classifiers also deemed venue to be the most
important feature by a significant margin, but once again we saw little separation between the
other attribute weights.
In search of better performance, we pursued a custom-built approach wherein we
created a neural net using TensorFlow and Keras. We suspected we might achieve better
predictive performance by sacrificing interpretability, but we were disappointed. We explored
with different dropout rates, adding more layers, normalized our “minimum ticket price
feature”, and adjusting the activation function used in our hidden, but our performance peaked
with an R 2 of 0.18. We believe the neural net was ineffective compared to our tree-based
approaches primarily due to the size of our dataset; the trees outperformed our neural net
because they employ a combination of simple techniques which do not require as much data as
deep learning.
Considering our results in their totality, we are left to conclude that we did not have
sufficient data to build a more effective classifier. We base this conclusion both on our own
intuition as well as the results we obtained. Regarding the former, we expect that an
individual’s decision to attend a show at the Theater depends not only on the merits of that
show, but also a) what other shows may be playing at other theaters, b) whether they were
aware of the show / how the show has been advertised, and c) the real cost of attending the
show. We were unable to capture these variables, and we believe that hampered our
effectiveness.
In conclusion, we produced a classifier that could predict the success of a show at the
Theater with a degree of accuracy high enough to be useful but not enough to be completely
confident in its predictions. We are pleased with the result, both because our goal at the outset
was to provide some utility through predictive power and because we did not have the data
necessary for deeper analysis. In the end, our random forest and MP’ classifiers achieved R 2 just
below 0.6 and RMS of nearly 0.13. While we might ideally want an R 2 approaching 1, we believe
our 0.6 value to be useful because it represents a significant improvement over the benchmark
established by ZeroR, which we thought was a high standard to surpass given the low variance
of our data.
In the effort contributing to this analysis, Harper performed yeoman’s work in
meticulously building the datasets, Brandon shouldered a tremendous burden in managing the
sprawling analysis, and Michael ventured daringly into the unknown as he pioneered our efforts
to visualize and report on our analysis. Looking forward, we would relish an opportunity to
attempt this analysis with a larger, more comprehensive dataset, especially one with precise
price data. We would also consider developing some kind of metric to capture the availability
of alternative, non-Theater entertainment options, as well as capturing the zeitgeist
surrounding a show as a means of determining public awareness of the production. With these
data, or simply a vastly larger corpus of data, we believe we could further elevate the accuracy of our models
</p>

