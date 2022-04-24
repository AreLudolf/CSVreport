#!/usr/bin/env python


def fileread():
    with open("eksempel_input.txt", "r", encoding="utf-8") as file:
        line_list = []
        for line in file:
            line_list = [entry.strip() for entry in line.split(",")]
            return(line_list)
