#!/usr/bin/env python
'''
Funksjon som leser gjennom fil linje for linje, deler opp og legger verdier inn i list
Filnavn er midlertidig hardkodet, skal leses fra parameter input
'''
def fileread():
    with open("eksempel_input.txt", "r", encoding="utf-8") as file:
        #trenger sikkert ikke å definere variabelen utenfor for-løkka i python, men det skader ikke
        line_list = []
        for line in file:
            line_list = [entry.strip() for entry in line.split(",")]
            return(line_list)
