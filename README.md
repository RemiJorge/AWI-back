<div align="center">

# Volunteer Management Platform Backend

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

---

French version of this : [README.fr.md](README.fr.md)
<a href="README.fr.md"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Flag_of_France.svg/1200px-Flag_of_France.svg.png" width="20" height="15" alt="French version"></a>

---

### **Description**

This is a volunteer management platform backend for the Games Week event in Montpellier. 

---

[Installation and Execution](#installation) •
[Documentation](#documentation) •
[Contributions](#contributions)

**Please read the the thourough [Documentation](Documentation.pdf) provided.**
</div>


## Main Features

- Volunteers can consult the inscriptions planning and decide which activity they want to participate in, consult the different games available, message the responsible of the activities and manage their profile.
- Admins can manage the inscriptions, festivals, activities, and import new games through a CSV file.
- Highly secure with regards to the latest security standards, including GDPR compliance.


## Table of Contents

- [Installation](#installation)
  - [Pre-requisites](#pre-requisites)
  - [Virtual environment](#virtual-environment)
- [Documentation](#documentation)
  - [Folder structure](#folder-structure)
- [Contributions](#contributions)
  - [Authors](#authors)
  - [Version control](#version-control)

# Installation
<sup>[(Back to top)](#table-of-contents)</sup>

## Pre-requisites
<sup>[(Back to top)](#table-of-contents)</sup>

You need python 3.10 or higher installed on your machine.

## Virtual environment
<sup>[(Back to top)](#table-of-contents)</sup>

Create virtual environment:

```bash
python3 -m venv env
```

Activate virtual environment (Linux):

```bash
source env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

# Documentation
<sup>[(Back to top)](#table-of-contents)</sup>

A thourough documentation is provided in the [Documentation](Documentation.pdf) file.


## Folder structure
<sup>[(Back to top)](#table-of-contents)</sup>

The project is structured as follows:
```bash
.
├── app
│   ├── controllers
│   │   ├── auth_controller.py
│   │   ├── festival_controller.py
│   │   ├── file_controller.py
│   │   ├── inscription_controller.py
│   │   ├── item_controller.py
│   │   ├── message_controller.py
│   │   ├── poste_controller.py
│   │   ├── referent_controller.py
│   │   └── user_controller.py
│   ├── database
│   │   ├── db.py
│   │   └── db_session.py
│   ├── models
│   │   ├── auth.py
│   │   ├── festival.py
│   │   ├── file.py
│   │   ├── inscription.py
│   │   ├── item.py
│   │   ├── message.py
│   │   └── user.py
│   ├── routers
│   │   ├── auth_router.py
│   │   ├── festival_router.py
│   │   ├── file_router.py
│   │   ├── inscription_router.py
│   │   ├── items_router.py
│   │   ├── message_router.py
│   │   ├── poste_router.py
│   │   ├── referent_router.py
│   │   └── user_router.py
│   └── sql
│       ├── auth.sql
│       ├── inscription.sql
│       ├── items.sql
│       ├── message.sql
│       └── referents.sql
├── LICENSE.txt
├── main.py
├── README.fr.md
├── README.md
└── requirements.txt
```

# Contributions
<sup>[(Back to top)](#table-of-contents)</sup>

## Authors
<sup>[(Back to top)](#table-of-contents)</sup>

- [**Alexandre Deloire**](https://github.com/alexdeloire)
- [**Remi Jorge**](https://github.com/RemiJorge)

## Version control
<sup>[(Back to top)](#table-of-contents)</sup>

Git is used for version control.