---
layout: page
title: Predicting the Success of a Theatrical Production
permalink: /MLproject/
---
###### Created by: Harper Pack, Brandon Harris and Michael Cantu

###### ABSTRACT
<a href="Airbnb.pdf" download="../Documents/GitHub/michaelcan2.github.io/Airbnb.pdf">Click here to download PDF</a>

<p> 
We sought to predict the success of a show at one of Chicago’s premier theater companies (hereafter the “Theater”; actual name withheld at the request of the institution).  Our task is an important one insofar as its successful completion could provide material support to the Theater, which is a significant thread in the cultural fabric of Chicago.  It is incumbent upon such cultural institutions to ensure they remain both financially viable and socially relevant.  We believe the ability to anticipate the success of a show prior to investing in its production would help the Theater in its pursuit of these goals.
</p>

<p> 
The Theater shared with us data listing performance dates and tickets sold, and through research and perseverance we developed features for season, daypart, genre, venue, minimum ticket price, production length, national origin of the production, recurring productions, and family-oriented productions.  We chose percentage of seats sold as our classification variable, and thus we favored learners that promised good performance with classification using continuous variables.  We experimented with k-nearest neighbor, linear regression, additive regression, random forests, m-5-prime, and neural networks.  Random forests and m-5-prime produced the best results, with R2 values of 0.59 and 0.58 and root-mean-squared errors of .131 and .132, respectively.  Looking ahead to future work, we believe better results will require more data.  In particular, we think more ticket pricing and marketing/advertising data would be especially valuable. 
</p>

 <img src='../img/biggergraph.jpg' width="500" height="600"> 
 <em>Figure 1 above illustrates our M5' tree. 
 <b>Please right click image to open in new tab to zoom in.
<!--  <img class="picbig" src='../img/biggergraph.jpg' alt="big"> -->


