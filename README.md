# Project One: Poetry Web App

## Overview

**Project One** is a full-stack Flask web application that allows users to register, log in, and post, view, comment on, edit, and delete original poems. The app uses:

- **Flask** for the web server
- **MySQL (RDS)** for relational data storage (poems, comments)
- **DynamoDB** for user authentication and account storage
- **AWS Services** such as IAM, VPC, and RDS for secure, scalable cloud infrastructure

## Features

- Create, read, update, and delete poems
- Add and delete comments per poem
- User registration and login with DynamoDB
- SQL JOINs to fetch poem-comment-author relationships
- Authentication check before accessing pages
- AWS-based deployment using RDS and IAM best practices
.gitignore hides sensitive credentials



# Dependencies 
Flask
boto3
botocore
pymysql
(this all can be found in the requirements.txt file

# credit and Licensing Info
Educational Purpose only

# Auther
Morgan Kaponga
