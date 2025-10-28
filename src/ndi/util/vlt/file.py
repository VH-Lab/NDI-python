import os
import re
from .string import strcmp_substitution

def dirstrip(ds):
    """
    Removes '.', '..', '.DS_Store', and '.git' from a directory listing.
    """
    return [d for d in ds if d.name not in ['.', '..', '.DS_Store', '.git']]

def findfilegroups(parentdir, fileparameters, **kwargs):
    """
    Finds groups of files based on parameters.
    """
    search_depth = kwargs.get('SearchDepth', float('inf'))
    search_parent_first = kwargs.get('SearchParentFirst', True)
    search_parent = kwargs.get('SearchParent', True)

    filelist = []

    if search_depth < 0:
        return filelist

    subdirs = []
    regularfiles = []
    try:
        with os.scandir(parentdir) as it:
            for entry in it:
                if entry.is_dir():
                    subdirs.append(entry.name)
                else:
                    regularfiles.append(entry.name)
    except FileNotFoundError:
        return filelist

    if not search_parent_first:
        for subdir in subdirs:
            filelist.extend(findfilegroups(os.path.join(parentdir, subdir), fileparameters, **kwargs))

    if search_parent:
        filelist_potential = []

        tf, match_string, search_string = strcmp_substitution(fileparameters[0], regularfiles, **kwargs)

        for i, t in enumerate(tf):
            if t:
                filelist_potential.append({'searchString': search_string[i], 'filelist': [match_string[i]]})

        for k in range(1, len(fileparameters)):
            new_filelist_potential = []
            for j in range(len(filelist_potential)):
                kwargs['SubstituteString'] = filelist_potential[j]['searchString']
                tf, match_string, new_search_string = strcmp_substitution(fileparameters[k], regularfiles, **kwargs)

                for i, t in enumerate(tf):
                    if t:
                        matchpotential = {}
                        if not filelist_potential[j]['searchString']:
                            matchpotential['searchString'] = new_search_string[i]
                        else:
                            matchpotential['searchString'] = filelist_potential[j]['searchString']
                        matchpotential['filelist'] = filelist_potential[j]['filelist'] + [match_string[i]]
                        new_filelist_potential.append(matchpotential)

            filelist_potential = new_filelist_potential
            if not filelist_potential:
                break

        for j in range(len(filelist_potential)):
            myfilelist = []
            for k in range(len(filelist_potential[j]['filelist'])):
                myfilelist.append(os.path.join(parentdir, filelist_potential[j]['filelist'][k]))
            filelist.append(myfilelist)

    if search_parent_first:
        kwargs['SearchDepth'] = search_depth - 1
        for subdir in subdirs:
            filelist.extend(findfilegroups(os.path.join(parentdir, subdir), fileparameters, **kwargs))

    return filelist
