# What is it?

It is a web application that can predict the value of a diamond based on its characteristics. And also this is my first try of developing a full-cycle application using machine learning (based on this [guide](https://github.com/pycaret/deployment-heroku)). Just follow the link (it may take a long time to load), enter the data (or use the ones already entered) and get the cost of the diamond.

Application: **["How Big Is Love"](https://how-big-is-love.herokuapp.com/)**

*и немного по русски: это моя первая попытка сделать не просто тетрадку в юпитере, а полностью цикл разработки машинного обучения. Выше ссылка, ниже использованный датасет и технологии*

# Dataset

For this Application I used a dataset based on a case study called "Sarah Gets a Diamond". This case was presented in the first year decision analysis course at Darden School of Business (University of Virginia). The basis for the data is a case regarding a hopeless romantic MBA student choosing the right diamond for his bride-to-be, Sarah. The data contains 6000 records for training. Short descriptions of each column are as follows:

- ID: Uniquely identifies each observation (diamond)
- Carat Weight: The weight of the diamond in metric carats. One carat is equal to 0.2 grams, roughly the same weight as a paperclip
- Cut: One of five values indicating the cut of the diamond in the following order of desirability (Signature-Ideal, Ideal, Very Good, Good, Fair)
- Color: One of six values indicating the diamond's color in the following order of desirability (D, E, F - Colorless, G, H, I - Near colorless)
- Clarity: One of seven values indicating the diamond's clarity in the following order of desirability (F - Flawless, IF - Internally Flawless, VVS1 or VVS2 - Very, Very Slightly Included, or VS1 or VS2 - Very Slightly Included, SI1 - Slightly Included)
- Polish: One of four values indicating the diamond's polish (ID - Ideal, EX - Excellent, VG - Very Good, G - Good)
- Symmetry: One of four values indicating the diamond's symmetry (ID - Ideal, EX - Excellent, VG - Very Good, G - Good)
- Report: One of of two values "AGSL" or "GIA" indicating which grading agency reported the qualities of the diamond qualities
- Price: The amount in USD that the diamond is valued Target Column

Dataset Acknowledgement:

This case was prepared by Greg Mills (MBA ’07) under the supervision of Phillip E. Pfeifer, Alumni Research Professor of Business Administration. Copyright (c) 2007 by the University of Virginia Darden School Foundation, Charlottesville, VA. All rights reserved.

The original dataset and description can be found [here](https://github.com/DardenDSC/sarah-gets-a-diamond)

# Tech

Upload to [heroku](https://dashboard.heroku.com/apps).  


Made with [Flask](https://flask.palletsprojects.com/en/2.0.x/) and [pyCaret](https://pycaret.org/)
