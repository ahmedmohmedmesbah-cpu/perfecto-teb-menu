# PYTHON MANAGEMENT APPLICATION (CMS)

Build a complete desktop Content Management System (CMS) for the Perfecto Digital Menu.

This application is the ONLY administration tool used to manage the website.

The administrator must NEVER edit HTML, CSS, JavaScript, JSON, or image folders manually.

The application should provide a modern graphical interface where every operation can be completed through buttons, forms, tables, and dialogs.

The application should be designed as a professional commercial desktop application, not a simple utility.

====================================================
TECHNICAL REQUIREMENTS
====================================================

Programming Language:
Python 3.12+

GUI Framework:
CustomTkinter (Preferred)

Architecture:
Object-Oriented Programming (OOP)

Design Pattern:
Modular architecture with separated components.

Suggested modules:

- Main Application
- Dashboard
- Product Manager
- Category Manager
- Excel Import / Export
- Image Manager
- JSON Manager
- Backup Manager
- Settings
- Utility Functions

Requirements:

- Clean code
- Modular code
- Well documented
- Fully commented
- Exception handling
- Logging system
- Easy future expansion

The application must run completely offline.

====================================================
GENERAL PURPOSE
====================================================

The application manages every piece of information displayed on the website.

The website only reads data.

The Python application writes and maintains the data.

Every change made inside the application must automatically update the JSON database.

No manual editing of files should ever be required.

====================================================
MAIN WINDOW
====================================================

The main window should include:

Top Toolbar

Left Navigation Panel

Dashboard

Product Manager

Category Manager

Excel Import / Export

Backup Manager

Settings

About

Status Bar

====================================================
DASHBOARD
====================================================

The dashboard should display:

Total Products

Total Categories

Products With Images

Products Without Images

Available Products

Unavailable Products

Last Save Time

Last Backup Time

JSON Database Status

Website Folder Status

====================================================
PRODUCT MANAGEMENT
====================================================

The Product Manager is the core of the application.

Display all products inside a professional table.

Columns:

Product ID

Thumbnail

Product Name

Category

Price

Selling Unit

Status

Image

Last Modified

Support:

Sorting

Searching

Filtering

Multi Selection

Column Resize

Double Click Edit

Context Menu

====================================================
PRODUCT INFORMATION
====================================================

Each product should contain:

Unique Product ID

Arabic Product Name

Category

Price

Selling Unit

Availability Status

Image Filename

Image Path

Created Date

Modified Date

====================================================
SELLING UNITS
====================================================

Supported units:

قطعة

كيلو

جرام

لتر

مل

علبة

كيس

زجاجة

ربطة

رول

نصف كيلو

ربع كيلو

====================================================
PRODUCT STATUS
====================================================

Every product has a Status.

Supported values:

متوفر

غير موجود حاليا

Inside the application:

Display status using colored badges.

Green

متوفر

Gray

غير موجود حاليا

Allow changing status from:

Dropdown

Toggle Switch

Bulk Operations

Context Menu

Support filtering by status.

====================================================
PRODUCT OPERATIONS
====================================================

The administrator can:

Add Product

Edit Product

Delete Product

Duplicate Product

Copy Product

Move Product

Enable Product

Disable Product

Change Status

Change Price

Change Unit

Change Category

Change Image

Remove Image

Preview Image

Search

Sort

Filter

====================================================
ADD / EDIT PRODUCT WINDOW
====================================================

Fields:

Product Name

Category

Price

Selling Unit

Status

Image

Buttons:

Browse Image

Remove Image

Save

Cancel

Live Image Preview

Validation before saving.

====================================================
CATEGORY MANAGER
====================================================

Allow administrators to:

Create Category

Rename Category

Delete Category

Reorder Categories

Merge Categories

Move Products Between Categories

Show Product Count

Categories should automatically synchronize with the JSON database.

====================================================
IMAGE MANAGER
====================================================

The application manages all product images.

When selecting an image:

Automatically copy it into:

assets/images/

Automatically rename duplicate filenames.

Generate safe filenames.

Update JSON automatically.

Create thumbnails.

Preview images.

Support:

JPG

PNG

WEBP

JPEG

If no image exists:

Use placeholder image.

====================================================
SEARCH SYSTEM
====================================================

Instant Search.

Search by:

Product Name

Category

Status

Price

Support live filtering while typing.

====================================================
FILTERS
====================================================

Filters:

All Products

Available Products

Unavailable Products

Products With Images

Products Without Images

Category

Selling Unit

====================================================
BULK OPERATIONS
====================================================

Support selecting multiple products.

Available operations:

Delete

Duplicate

Change Category

Change Status

Change Selling Unit

Export

Print

====================================================
EXCEL IMPORT / EXPORT
====================================================

The application must support Excel Import and Export.

Excel format:

.xlsx

The purpose is allowing the store owner to update products quickly using Microsoft Excel.

====================================================
EXPORT
====================================================

Administrator can export:

One Category

Multiple Categories

All Categories

When exporting all categories:

Generate one Excel workbook.

Each worksheet represents one category.

Example:

Perfecto_Products.xlsx

Worksheets:

منتجات ألبان

منتجات لحوم

مجمدات

مشروبات

منظفات

حلويات

Each worksheet contains only three editable columns.

Product Name

Product Price

Selling Unit

The Excel sheets should be professionally formatted.

Requirements:

Bold Header

Table Formatting

Auto Column Width

Freeze Header

RTL Layout

Arabic Font

====================================================
IMPORT
====================================================

The application must import the same workbook.

During import:

Match products using Product Name.

Update:

Price

Selling Unit

If product does not exist:

Automatically create it.

If category does not exist:

Automatically create it.

Preserve:

Images

Status

Product IDs

Created Date

Modified Date

Validate before importing.

Detect:

Missing Columns

Duplicate Products

Invalid Prices

Invalid Units

Empty Product Names

Display an import summary.

Example:

Products Updated

Products Added

Products Skipped

Errors Found

Allow confirmation before importing.

Always create backup before import.

====================================================
JSON MANAGEMENT
====================================================

The JSON file is the only database.

Requirements:

UTF-8 Encoding

Pretty Formatting

Proper Indentation

Automatic Validation

Automatic Repair when possible

Prevent Corruption

Atomic Save Operations

====================================================
BACKUP SYSTEM
====================================================

Before every save:

Automatically create backup.

Store backups inside:

backup/

Example:

products_2026-07-31_15-40.json

Provide Backup Manager.

Functions:

View Backups

Restore Backup

Delete Backup

Export Backup

====================================================
SETTINGS
====================================================

Allow changing:

Website Folder

JSON Location

Images Folder

Backup Folder

Theme

Language

Auto Save

Image Quality

Thumbnail Size

====================================================
LOGGING
====================================================

Maintain log files.

Log:

Errors

Warnings

Import Operations

Export Operations

Save Operations

Backup Operations

====================================================
VALIDATION
====================================================

Validate before every save.

Rules:

Product Name Required

Price Numeric

Category Required

Selling Unit Valid

Unique Product ID

Valid Image Path

No Duplicate IDs

No Corrupted JSON

====================================================
USER EXPERIENCE
====================================================

The application should feel like professional inventory management software.

Requirements:

Modern UI

Responsive Layout

Light Theme

Perfecto Brand Colors

Rounded Components

Smooth Animations

Keyboard Shortcuts

Undo Support

Redo Support

Confirmation Dialogs

Loading Indicators

Progress Bars

Success Notifications

Error Notifications

Warning Messages

====================================================
SAVE PROCESS
====================================================

When Save is pressed:

Validate Data

Create Backup

Save JSON

Refresh Internal Data

Display Success Message

No data should ever be lost during save.

====================================================
WORKFLOW
====================================================

Open Python Application

↓

Import Excel (Optional)

↓

Manage Categories

↓

Manage Products

↓

Manage Images

↓

Update Prices

↓

Update Product Status

↓

Save

↓

JSON Database Updated

↓

Open GitHub Desktop

↓

Commit

↓

Push

↓

GitHub Pages Automatically Publishes The Updated Website

====================================================
FUTURE EXPANSION
====================================================

The architecture must be designed to support future modules without redesign.

Possible future modules:

Barcode Scanner

QR Code Generator

Inventory Quantity

Offers Manager

Discount Manager

Branch Management

Multi-language Support

Cloud Synchronization

GitHub API Auto Publish

Automatic Price History

Analytics Dashboard

Sales Reports

Product Expiration Tracking

Supplier Management

Customer Notifications

The application should be developed as production-quality software with clean architecture, high maintainability, and scalability suitable for managing thousands of products.