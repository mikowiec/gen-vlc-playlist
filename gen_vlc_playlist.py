import xml.etree.ElementTree as xml
import os
import pprint
#import inspect
#from itertools import groupby
import re

# **********************************************************************************
# Settings
ext_list = ['.mp4', '.mkv', '.avi', '.flv', '.mov', '.wmv', '.vob', '.mpg','.3gp', '.m4v', '.ts']       #List of extensions to be checked.
#
check_subdirectories = True #False        #Set false to get files only from cwd.
check_sort_file_prefix4 = True      # sort files with prefix ('1. file', `10. file', '100. file')
pat_sort_file_prefix4 = r"\/\d+\."  # regex pattern
check_playlist_web = True
addr_playlist_web = 'http://192.168.1.1:8080'

# **********************************************************************************


class Playlist:
    """Build xml playlist."""
    
    def __init__(self):
    #Defines basic tree structure.
        self.playlist = xml.Element('playlist')
        self.tree = xml.ElementTree(self.playlist)
        self.playlist.set('xmlns','http://xspf.org/ns/0/')
        self.playlist.set('xmlns:vlc','http://www.videolan.org/vlc/playlist/ns/0/')
        self.playlist.set('version', '1')

        self.title = xml.Element('title')
        self.playlist.append(self.title)
        self.title.text = 'Playlist' 

        self.trackList = xml.Element('trackList')
        self.playlist.append(self.trackList)

    def add_track(self, path):
    #Add tracks to xml tree (within trackList).
        track = xml.Element('track')
        location = xml.Element('location')
        location.text = path
        track.append(location)
        self.trackList.append(track)
    
    def get_playlist(self):
    #Return complete playlist with tracks.
        return self.playlist

class Videos:
    """Manage files (videos) to be added to the playlist."""
    def __init__(self):
        pass

    def remove_nonvideo_files(self,file_list):
    #Removes files whose extension is not mentioned in ext_list from list of files.
        for index,file_name in enumerate(file_list[:]):
            #if file_name.endswith(tuple(ext_list)) or file_name.endswith(tuple(ext_list.upper())) :
            if file_name.endswith(tuple(ext_list)) or file_name.endswith(tuple(ext.upper() for ext in ext_list)):
                pass
            else:
                file_list.remove(file_name)
        return file_list
    
    # `C:\Users` to `file:///C:/Users`
    def edit_paths(self, video_files):
    #Add path and prefix to files as required in vlc playlist file. 
        for index in range(len(video_files)):
            video_files[index] =( 
            'file:///' + os.path.join(video_files[index])).replace('\\','/')
        return video_files
    
    def get_videos(self):
    #Returns list of video files in the directory.
        if check_subdirectories == True:
            pathlist = [os.getcwd()]    #List of all directories to be scanned.
            for root, dirs, files in os.walk(os.getcwd()):
                for name in dirs:
                        subdir_path = os.path.join(root, name)
                        if subdir_path.find('\.') != -1:    #Excludes hidden directoriess.
                            pass
                        else:
                            pathlist.append(subdir_path)
                            
            videos = []
            #Loops through files of root directory and every subdirectory.
            for path in pathlist:
                all_files = os.listdir(path)
                for f in self.remove_nonvideo_files(all_files):
                    location = path+ '\\' + f
                    videos.append(location)
            return videos
            
        else:
            videos = []
            all_files = os.listdir()
            for f in self.remove_nonvideo_files(all_files):
                    location = os.getcwd() + '\\' + f
                    videos.append(location)
            return videos
    
    # !!nk: different sorting
    def sort_videos(self, video_files):
        # sort files with prefix ('1. file', `10. file', '100. file')
        if check_sort_file_prefix4:
            mo = re.compile(pat_sort_file_prefix4)
            # _T/www2/24. Предварител
            #        _  _ # exclude first and last when group
            video_files.sort(key=lambda x: int(mo.search(x).group()[1:-1] ) )
            #print(video_files)
            return video_files
        
    
    # `C:\Users\videos` to `http://addr:port/videos`
    def web_paths(self, video_files):
    #Add server addr to files as required in vlc playlist file. 
        web_files = []
        # root directory for web server - current directory
        webroot = ('file:///' + os.getcwd() ).replace('\\','/')
        # 
        for index in range(len(video_files)):
            file_url = (addr_playlist_web + video_files[index]).replace(webroot, '')
            web_files.append(file_url)
        return web_files



def printobj(xobj):
    #ok
    for item in xobj:
        print(item)



def main():
    playlist = Playlist()
    playlist_web = Playlist()
    videos = Videos()
    

    video_files = videos.get_videos()
    video_paths = videos.edit_paths(video_files)
    video_sorted = videos.sort_videos(video_paths)
    web_files = videos.web_paths(video_sorted)
    
    # write song.xspf local playlist   
    for path in video_sorted:    # video_paths
        playlist.add_track(path)
    #
    playlist_xml = playlist.get_playlist()
    with open('songs.xspf','w') as mf:
        mf.write(xml.tostring(playlist_xml).decode('utf-8'))

    # write songweb.xspf web playlist   
    for path in web_files:    # video_paths
        playlist_web.add_track(path)
    #
    playlist_xml = playlist_web.get_playlist()
    with open('songsweb.xspf','w') as mf:
        mf.write(xml.tostring(playlist_xml).decode('utf-8'))




    
main()

'''
playlist(ROOT)
    title /title
    trackList
        track
            location file:///path /location
            title                 /title
            image                 /image
            duration              /duration
        /track
    /tracklist
/playlist
'''
