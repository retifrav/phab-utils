This is a special module for performing particular tasks. Those often combine functionality of different utility modules to execute a complex multistep procedure.

An example of such task can be the following: "*Find all the planetary systems in the NASA Exoplanet Archive that have at least 2 planets (both of which should have a known mass and radius) and enrich the resulting dataset by adding missing values based on the data from Paris Astronomical Data Centre database*".

At first the code in this module might contain functions that duplicate some of the already implemented functionality from utility modules, but going forward such duplicated code should be replaced by / moved out to utility modules.
