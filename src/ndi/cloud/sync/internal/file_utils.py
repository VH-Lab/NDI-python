import os

def get_file_uids_from_documents(ndi_documents):
    """
    Extracts all unique file UIDs from a list of NDI documents.
    """
    file_uids_list = []
    if not ndi_documents:
        return []

    for document in ndi_documents:
        if hasattr(document, 'has_files') and document.has_files(): # Assuming document object structure
             # document.document_properties is a dict
             file_info = document.document_properties.get('files', {}).get('file_info', [])
             for info in file_info:
                 locations = info.get('locations', [])
                 for location in locations:
                     uid = location.get('uid')
                     if uid:
                         file_uids_list.append(uid)

    return list(set(file_uids_list))

def update_file_info_for_local_files(document, file_directory):
    """
    Update file info of document for local files.
    """
    if hasattr(document, 'has_files') and document.has_files():
        # This part requires deeper knowledge of ndi.document methods like reset_file_info and add_file
        # Assuming we can manipulate document_properties directly as per python port pattern
        # The Matlab code uses document methods. Python Document class in this repo:
        # has document_properties dict.
        # But methods like `reset_file_info` and `add_file` might not be ported yet or available in `did.document`.
        # I checked `src/ndi/document.py` and it inherits from `did.document.Document`.
        # I should check `did.document.Document`.
        # For now, I will implement logic manipulating `document_properties`.

        file_info = document.document_properties.get('files', {}).get('file_info', [])
        # In Matlab: document = document.reset_file_info();
        # We need to replicate this logic.

        # Simulating reset: clear locations or rebuild?
        # Matlab loop:
        # for i = 1:numel(originalFileInfo)
        #    file_uid = originalFileInfo(i).locations(1).uid;
        #    file_location = fullfile(fileDirectory, file_uid);
        #    ...

        new_file_info = []
        for info in file_info:
            if 'locations' in info and info['locations']:
                file_uid = info['locations'][0].get('uid')
                if file_uid:
                    file_location = os.path.join(file_directory, file_uid)
                    if os.path.isfile(file_location):
                        # Construct new file info entry compatible with add_file
                        # Matlab add_file(filename, file_location)
                        # We just update the existing entry to point to local file
                        # This might differ from "reset and add".
                        # Ideally we should use the Document methods if they exist.
                        # Assuming they don't, we update the dict.

                        # Resetting locations to just this local file
                        info['locations'] = [{
                            'location': file_location,
                            'location_type': 'file', # Assuming local file type
                            'uid': file_uid
                        }]
                    else:
                        print(f'Warning: Local file does not exist for document "{document.document_properties["base"]["id"]}"')
            new_file_info.append(info)

        document.document_properties['files']['file_info'] = new_file_info
    return document

def update_file_info_for_remote_files(document, cloud_dataset_id):
    """
    Update file info of document for remote (cloud-only) files.
    """
    if hasattr(document, 'has_files') and document.has_files():
        file_info = document.document_properties.get('files', {}).get('file_info', [])

        for info in file_info:
            if 'locations' in info and info['locations']:
                # Replace/override 1st file location
                loc = info['locations'][0]
                loc['delete_original'] = 0
                loc['ingest'] = 0

                file_uid = loc.get('uid')
                if file_uid:
                    file_location = f'ndic://{cloud_dataset_id}/{file_uid}'
                    loc['location'] = file_location
                    loc['location_type'] = 'ndicloud'

        document.document_properties['files']['file_info'] = file_info
    return document
