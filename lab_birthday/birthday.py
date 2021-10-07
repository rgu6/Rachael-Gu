#
# Hi! :)
# - This is NOT the lab file, you can find that in lab_birthday.ipynb
# - This is the source code for the `birthday` library.
#        ...you'll know how everything in here works in about 3 weeks!
#        (Notice we're doing this just with pandas and random -- you already know about those!)
#

import pandas as pd
import random

def myBirthday(n):
  return 1 - (364 / 365)**n

def myBirthday_DataFrame(n):
  # Create a new empty list, append `n` results to it:
  results = []
  for i in range(n):
    results.append( {'Other People': i, 'P(n)': myBirthday(i) } )
      
  # Create a DataFrame out of that list:
  return pd.DataFrame( results )


def sharedBirthday(n):
  prod = 1
  for i in range(1, n):
    prod = prod * (365 - i) / 365
  return 1 - prod  

def sharedBirthday_DataFrame(n):
  # Create a new empty list, append `n` results to it:
  results = []
  for i in range(n):
    results.append( {'People at The Party': i, 'P(n)': sharedBirthday(i) } )
      
  # Create a DataFrame out of that list:
  return pd.DataFrame( results )


def forTaylor():
  ct = 0   #< Count the number of people needed
  day = 0  #< Count the current unique days found
  
  # While all 365 unique days have not been seen:
  while day < 365:
    # Add a person:
    ct = ct + 1
    
    # Check if a random number is a new, unique day.
    # - When day == 0, we've seen no unique days so P(unique day) == 1 as randint(0, 364) will always be `>= 0` (100%)
    # - When day == 1, P(unique day) == (364/365) and we check if we get a number `>= 1` (any number but 0)
    # - When day == 2, P(unique day) == (363/365) and we check if we get a number `>= 2` (anything but 0 or 1)
    # - ...
    # - When day == 364, P(unique day) == (1/365) so we need get randint(0, 364) to be exactly 364.
    if random.randint(0, 364) >= day:
      day = day + 1
          
  # Return the number of people needed
  return ct

def forTaylor_DataFrame(n):
  # Create a new empty list, append `n` results to it:
  results = []
  for i in range(n):
    results.append( {'people': forTaylor() } )
      
  # Create a DataFrame out of that list:
  return pd.DataFrame( results )


def forOlivia():
  ct = 0   #< Count the number of people needed
  day1 = 0  #< Count the current unique days found for the first person with the birthday
  day2 = 0  #< Count the current unique days found for the second person with the birthday
  
  # While all 365 unique days have not been seen:
  while (day1 < 365) | (day2 < 365):
    # Add a person:
    ct = ct + 1
    
    # Check if a random number is a new, unique day.
    # - When day == 0, we've seen no unique days so P(unique day) == 1 as randint(0, 364) will always be `>= 0` (100%)
    # - When day == 1, P(unique day) == (364/365) and we check if we get a number `>= 1` (any number but 0)
    # - When day == 2, P(unique day) == (363/365) and we check if we get a number `>= 2` (anything but 0 or 1)
    # - ...
    # - When day == 364, P(unique day) == (1/365) so we need get randint(0, 364) to be exactly 364.
    birthday = random.randint(0, 364)
    if birthday >= day1:
      day1 = day1 + 1
    elif birthday >= day2:
      day2 = day2 + 1
          
  # Return the number of people needed
  return ct

def forOlivia_DataFrame(n):
  # Create a new empty list, append `n` results to it:
  results = []
  for i in range(n):
    results.append( {'people': forOlivia() } )
      
  # Create a DataFrame out of that list:
  return pd.DataFrame( results )
