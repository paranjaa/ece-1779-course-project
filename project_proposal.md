##  ECE 1779 Group Project Proposal

### 0\. Group Members

1003260918 \- David Zhang \- davidcw.zhang@mail.utoronto.ca

1008782364 \- Alok Paranjape \- alok.paranjape@mail.utoronto.ca

### 1\. Motivation

Across multiple commercial sectors, such as retail or logistics, there’s a distinct need for accurate and timely inventory management. Traditional paper-based management systems, and existing software solutions may be unable to provide detailed and up to the minute recordkeeping, which may be taxing on operational efficiency and profits. Additionally, analyzing and reporting statistics generally require a lot of manual labour when using traditional solutions. With this project, we intend to make a software solution that automatically handles inventory management, in a way that improves upon these qualities by using cloud computing. 

Due to the ubiquity of inventory management, there are a plethora of possible users of this system. For example, B2B companies such as Salesforce or B2C companies such as local grocery stores or restaurants, handle and move large amounts of inventory across the world. The volume of such transactions necessitates automated management of inventory and the diverse distribution of such logistics networks requires cloud computing with localized edge nodes to minimize latency and maximize data accessibility. Due to the top down nature of inventory management, while the customer base might include different companies and industries, the user base would include different levels of employees, such as managers and staff members.

Existing solutions, such as traditional paper management or accounting software solutions (such as Clover or Square) cannot keep up with the volume of transactions. Additionally, the management of inventory in real-time is infeasible when most of the work is still done by human operators. Market and inventory trend reports are used to properly direct the financial decisions within a company. Without these reports, the company may need to compensate with unnecessarily large stock buffers to avoid understocking. However, these reports are unattainable in real-time using traditional implementations. Thus, an automated, distributed, inventory management system is required. Such a system can set up inventory threshold mechanisms to automatically handle any deviations from set targets for every item. This system can also generate reports of the entire inventory on-demand. As such, the project could offer some substantial improvements over existing solutions.

### 2\. Objectives and Key Features

This project follows Example Project \#4 as a guideline.

* The system as a whole will be hosted on [Fly.io](http://Fly.io) to ensure high availability and low latency across multiple data regions. To promote rapid application development, we will develop the backend primarily with Python and then containerize it using Docker. These will then be orchestrated with Kubernetes to allow for dynamic autoscaling of each service independently.

* To support the inventory management system we will use PostGreSQL to robustly store the data. CRUD operations will be used to manage the inventory system by, respectively, adding/displaying/modifying/removing items from the system. 

* In order to be accessible, all of these operations will be actionable from a user-readable dashboard that queries through the Python backend and displays the inventory and permitted actions legibly as well as system health. This dashboard will also allow for fine-tuned searching and filtering of inventory by user-defined qualifiers. 

* Most notably, we will also have role-based access such that these operations will only be permitted should the user be assigned the appropriate role. This will include additional security enhancements, for authenticating and authorizing users. We will also periodically trigger automated backups of the database, and allow manual triggers, to ensure resiliency against data loss. 

* Finally, we will also have integrations that trigger outside of the dashboard, such as certain conditions being met (e.g. the quantity of an inventory item exceeding a set range) to send email notifications to the appropriate people, and real time stock updates.

To reiterate, this implementation fulfills the basic features required for the ECE1779 course project and implements auto-scaling of internal services, integration with external services, and handling authentication/authorization and secret management as advanced features.

### 3\. Tentative Plan

Due to the relatively short time frame of the project, rapid development is important. To that end, we will splitting the objectives and features up into more achievable blocks, in order to ensure development progresses efficiently:

|  | David Zhang | Alok Paranjape |
| :---- | :---- | :---- |
| Back-end Development | Set up the Python backend service to interface with PostGreSQL, and implement CRUD operations for inventory items (adding/removing, updating, etc) Dockerize the Python service | Implement PostGreSQL callbacks or notifications using Redis as an event-bus or using the TRIGGER keyword to allow integration of external alerting/monitoring services Dockerize and set up the Redis service if applicable |
| Front-end Development | Set up the dashboard for monitoring the health of the system using provider tools and metrics  | Set up the dashboard for monitoring inventory items, as well as searching and sorting items in the database |
| Security and Authentication | (Shared) Handle back-end support for authentication and authorization of users | (Shared) Handle front-end support for authentication and authorization of users |
| Deployment | Set up autoscaling of services using Kubernetes | Set up deployment on [Fly.io](http://Fly.io) and automate backups of database volumes |
| Other | (Shared) Write project documentation, and test existing features  | (Shared) Write project documentation, and test existing features  |

After the initial setup with the backend and dataset, the other blocks can be developed in parallel, with each team member taking a couple sections. We also intend to have weekly check-ins to monitor progress on different blocks and pivot should it be required.

