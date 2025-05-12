# Project Overview
Over the years, I’ve taken thousands of photos capturing special occasions, travels, and everyday moments. However, storing and retrieving these memories has become increasingly difficult. When I want to find a photo of a specific person, event, or location, I have no reliable way to search by these criteria. As a result, many meaningful moments are becoming harder to revisit simply because I can’t locate the images when I want them.

This project set out to solve that problem by creating a lightweight desktop application that allows all my photos to be stored in a single, unstructured folder, while enabling meaningful organisation and retrieval through tagging. I wanted the ability to add custom metadata to each image, such as the people present, the event, the location, and even the emotion it captures.

With this functionality, I can easily filter images to find exactly what I’m looking for. Whether it’s to reminisce about a particular trip, collect all the photos of a specific family member, or rediscover forgotten memories. The application is also designed as a digital photo album to enjoy with friends or relatives, allowing us to rediscover memories togetoger.

The project prioritises simplicity, privacy, and offline use. It is not designed for cloud syncing or large-scale deployment, but rather as a personal, private tool for preserving, organising, retrieving, and sharing cherished memories.

# System design
This section outlines the design requirements for the photo album application, focusing on what users need from the system and how the system should behave. It is divided into three parts: user requirements that describe the goals from the user's perspective, functional requirements that specify what the system shall do, and non-functional requirements that define the quality attributes of the system.

## User Requirements (UR)
- **UR1**: As a user, I want to search my photo album to **find memories of people or events quickly**.  
- **UR2**: As a user, I want to describe the content of my images so I can **organise my album efficiently**.  
- **UR3**: As a user, I want to apply the same description to multiple images at once to **save time while organising**.  
- **UR4**: As a user, I want to view image details (like people and events) to **remember when and where they were taken**.  
- **UR5**: As a user, I want to delete images so I can **clean up my album and save space**.  
- **UR6**: As a user, I want to see duplicate images so I can **clean up my album and save space**.  
- **UR7**: As a user, I want to easily copy selected images into a folder for **sharing with others**.  

## Functional Requirements
### 1. Tagging and Metadata Management
- **FR1.1** The system shall allow the user to add one or more tags to any image using a predefined set of categories:
  - People in the image  
  - Event  
  - Emotion  
  - Date  
  - Location
- **FR1.2** The system shall allow the user to leave one or more tag fields blank.
- **FR1.3** The system shall allow batch tagging operations (i.e., adding or removing tags from multiple images at once).
- **FR1.4** The system shall provide a tag management interface to:
  - View all tags added by the user during the current and previous sessions  
  - Rename existing user-added tags within the fixed categories  
  - Delete user-added tags that are no longer associated with any image  

### 2. Image Viewing
- **FR2.1** The system shall display all images in a user interface.
- **FR2.2** The system shall allow the user to view EXIF metadata (if available) associated with each selected image.

### 3. Search and Filtering
- **FR3.1** The system shall support filtering images by tag values entered under fixed categories (People, Event, Emotion, Date, Location).
- **FR3.2** The system shall allow combined filtering using multiple tag categories and additional criteria (e.g., images with missing tags).

### 4. Image File Operations and Sharing
- **FR4.1** The system shall support deleting images by moving them to a designated trash folder, rather than performing permanent deletion.
- **FR4.2** The system shall support copying a single selected image to a user-specified output folder.
- **FR4.3** The system shall support copying all currently filtered images to a user-specified output folder.

### 5. Persistence and State Management
- **FR5.1** The system shall maintain persistent storage of all user-added tags across sessions using a database or equivalent data store.
- **FR5.2** The system shall not persist automatically loaded tags or metadata.

### 6. Duplicate Image Detection
- **FR6.1** The system shall detect duplicate images based on file similarity or content comparison and present potential duplicates to the user.
- **FR6.2** The system shall allow the user to manually review duplicates and decide which image(s) to retain or delete.

## Non-Functional Requirements (NFR)
### 1. Usability
- **NFR1**: The system shall provide clear visual feedback when images are being loaded, filtered, or processed.
- **NFR2**: The interface shall be intuitive and require minimal instructions for a new user to begin organising images (~10 minutes of learning time).
- **NFR3**: The system shall provide clear visual feedback when images are selected, copied, or deleted.

### 2. Reliability and Fault Tolerance
- **NFR4**: The system shall preserve user-added tags and changes even in the event of an unexpected shutdown.
- **NFR5**: If an image fails to load, the system shall display a placeholder with a meaningful error message.

### 3. Data Persistence
- **NFR6**: All user-added tags shall persist across sessions without requiring manual saving.
- **NFR7**: Deleted images shall be moved to a trash folder and shall not be permanently removed unless explicitly confirmed by the user.

### 4. Compatibility
- **NFR8**: The application shall run on major desktop operating systems, including Windows, macOS, and Linux.

### 5. Privacy and Security
- **NFR9**: The system shall not require or initiate any internet connection for any feature or function.
- **NFR10**: The system shall not transmit image data, descriptions, or metadata outside the local environment without explicit user action (e.g., saving to a removable storage device).
- **NFR11**: Any file deletion or copying operation shall require user confirmation before being executed.

# Design Decisions

Initially, I planned to use ExifTool to edit metadata embedded directly within image files. While ExifTool works well for JPEGs and some other formats, it does not provide consistent support across all image types. Given that the photo album project needs to handle a variety of image formats, this approach proved limiting.

To overcome this, I chose a non-destructive, format-independent method: storing custom, searchable metadata in a separate database. This approach offers several advantages:

- **Format Independence**: Unlike embedded metadata, the database solution works uniformly across all image formats, ensuring compatibility without additional format-specific handling.
- **Non-Destructive**: The original image files remain untouched, preserving their integrity and preventing accidental corruption.
- **Searchability**: Metadata stored in a structured database can be efficiently queried, enabling fast filtering and retrieval.
- **Bulk Editing**: Updating metadata for multiple images becomes significantly easier when managed through a central system.
- **Structural Flexibility**: A custom database allows for evolving metadata schemas, supporting future changes without affecting existing data or image files.

This decision supports scalability, maintainability, and user convenience—key goals for the project.

# Technology
## Python Libraries and Tools
- **PyQt6** – for building the GUI.
- **SQLite** – used as the local database for storing metadata.

## Architecture Notes
The photo album application was developed using a simple, modular design that reflects its limited scope and focused purpose: to make photo tagging and filtering straightforward and user-friendly. The system was not intended to be scaled or deployed in complex environments, so the emphasis was placed on clarity, maintainability, and ease of use.

- **Object-Oriented Programming (OOP)**: Key components—such as image handling, metadata management, and user interface logic—were implemented as classes to improve separation of concerns and facilitate future updates.
- **Basic Application of the Single Responsibility Principle**: Functions and classes were generally written to perform a single, clearly defined task, which helps keep the code understandable and easier to debug.
- **Minimal External Dependencies**: Core functionality is implemented using standard Python libraries and PyQt6, making the application lightweight, portable, and easy to set up locally.
- **Readability Over Optimisation**: Code was written with an emphasis on readability rather than performance or scalability, in line with the project’s aim to be easy to maintain and adapt by others.

This pragmatic and lightweight architecture supports the project’s goal as a personal or small-scale photo organiser, while still allowing for modest future improvements or extensions.

# Future Work / Known Limitations
While the application meets its core goals, there are a few limitations in the current version and opportunities for future enhancements:
- **Video Format Support**: At present, the application is designed to work with image files only. Support for video files—such as tagging, thumbnail previews, and filtering—could be added in future versions to allow users to organise all their visual media in one place.
- **AI Tagging**: All tagging is currently manual. In future updates, computer vision techniques could be integrated to suggest tags automatically based on image content, such as recognising faces, scenes, or objects. This would significantly speed up the tagging process and help surface relevant metadata for older, forgotten images.
- **Undo Operations**: There is currently no undo functionality for deletions, tag edits, or batch operations. Introducing an undo/redo system would help prevent accidental data loss and give users more confidence when performing bulk edits or deletions.
- **File Renaming**: At present, the application does not support renaming image files. Providing the option to rename files—either manually or based on metadata—could improve consistency and make exported or shared files more meaningful.

These limitations were intentionally accepted to keep the initial system lightweight and easy to use. However, addressing them in future iterations could improve usability and extend the system's capabilities without compromising its core values of simplicity and privacy.

