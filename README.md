# Project Overview
Over the years, I’ve taken thousands of photos capturing special occasions, travels, and everyday moments. However, storing and retrieving these memories has become increasingly difficult. When I want to find a photo of a specific person, event, or location, I have no reliable way to search by these criteria. As a result, many meaningful moments are becoming harder to revisit simply because I can’t locate the images when I want them.

This project set out to solve that problem by creating a lightweight desktop application that allows all my photos to be stored in a single, unstructured folder, while enabling meaningful organisation and retrieval through tagging. I wanted the ability to add custom metadata to each image, such as the people present, the event, the location, and even the emotion it captures.

With this functionality, I can easily filter images to find exactly what I’m looking for, whether it’s to reminisce about a particular trip, collect all the photos of a specific family member, or rediscover forgotten memories. The application is also designed as a digital photo album to enjoy with friends or relatives, allowing us to rediscover memories together.

The project prioritises simplicity, privacy, and offline use. It is not designed for cloud syncing or large-scale deployment, but rather as a personal, private tool for preserving, organising, retrieving, and sharing cherished memories.

## Key Features
- Tag images with people, events, locations, emotions, and dates.
- Search and filter using multiple tag combinations.
- Detect and review duplicate images.
- Perform batch tagging and image operations.
- This app works fully offline. No data is transmitted over the internet. 

# Documentation
For full details on:
- [System & user requirements](https://github.com/shabaj-ahmed/photo_album/wiki/System-Requirements)
- [Design Decisions](https://github.com/shabaj-ahmed/photo_album/wiki/Design-Decisions)
- [Architectural decisions and database schema](https://github.com/shabaj-ahmed/photo_album/wiki/Architectural-decisions-and-database-schema)
- [Future features & limitations](https://github.com/shabaj-ahmed/photo_album/wiki/Future-Work)

👉 [Visit the project Wiki](https://github.com/shabaj-ahmed/photo_album/wiki)

# Python libraries Used
- **PyQt6** – Graphical user interface
- **SQLite** – Local metadata storage

# Getting Started

To install and run the app locally:

```bash
git clone https://github.com/shabaj-ahmed/photo_album.git
cd photo_album
python main.py
```
