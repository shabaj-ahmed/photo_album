# System design
This section outlines the design requirements for the photo album application, focusing on what users need from the system and how the system should behave. It is divided into three parts: user requirements that describe the goals from the user's perspective, functional requirements that specify what the system shall do, and non-functional requirements that define the quality attributes of the system.

## 🙋 User Requirements (UR)

- **UR1**: As a user, I want to search my photo album to **find memories of people or events quickly**.  
- **UR2**: As a user, I want to describe the content of my images so I can **organise my album efficiently**.  
- **UR3**: As a user, I want to apply the same description to multiple images at once to **save time while organizing**.  
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


# Technology

## **Python Library**

- PyQT6
- PyExifTool

# Setup
1. Install ExifTool system-wide
    - On macOS:
        '''
            brew install exiftool
        '''