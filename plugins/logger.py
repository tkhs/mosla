import os
import re
from slacklib import SlackPlugin
from datetime import datetime

class Logger( SlackPlugin ):

    def __init__( self, bot, klass_name ):
        super( Logger, self ).__init__( bot, klass_name )
        self.log_dir_path = "log"
        if not os.path.exists( self.log_dir_path ):
            os.mkdir( self.log_dir_path )

    def create_filename( self, channel ):
        return "_#" + channel.name + "-" + datetime.now().strftime( "%Y%m%d" ) + ".log"

    def create_timestamp( self ):
        return datetime.now().strftime( "%Y/%m/%d %H:%M:%S" )

    def create_log_line( self, user, channel, message ):
        timestamp = self.create_timestamp()
        line = timestamp + " #" + channel.name + " " + user.name + " > " + self.normalize_text( message )
        return line

    def normalize_mention( self, text ):
        mention_pattern = re.compile( r'<@([UW][0-9A-Z]{8})>' )
        for match in mention_pattern.finditer( text ):
            user = self.bot.users_list[ match.group( 1 ) ]
            text = text.replace( match.group( 0 ), "@" + user.name )
        return text

    def normalize_url( self, text ):
        mention_pattern = re.compile( r'<(https?://[^>]+)>' )
        for match in mention_pattern.finditer( text ):
            if match.group( 1 ).rfind( '|' ) < 0:
                str = match.group( 1 )
            else:
                full_url, short_url = match.group( 1 ).rsplit( '|', 1 )
                str = short_url
            text = text.replace( match.group( 0 ), str )
        return text

    def normalize_text( self, text ):
        text = self.normalize_mention( text )
        text = self.normalize_url( text )
        text = text.replace( '&amp;', '&' ).replace( '&lt;', '<' ).replace( '&gt;', '>' )
        return text

    def put_log( self, log_filename, text ):
        with open( self.log_dir_path + "/" + log_filename, "a", encoding="utf-8" ) as log_file:
            log_file.write( text + "\n" )

    def download_attachment_file( self ):
        pass

    def on_message( self, user, channel, message ):
        line = self.create_log_line( user, channel, message )
        log_filename = self.create_filename( channel )
        self.put_log( log_filename, line )