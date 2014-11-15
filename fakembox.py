'''
    __author__  = Ryan Stephany
    __date__    = 11Nov2014
    __owner__   = District Data Labs
    __purpose__ = SNA Workshop
'''


import sys
import mailbox
from faker import Faker
from numpy.random import randint
from time import strptime, gmtime
from loremipsum import get_sentences, generate_paragraph



class FakeMbox (object):
    ''' 
        This is a class that generates a fake mbox 
        email addresses are replaced with fake addresses
        subject is replace with a lorem ipsum sentence
        boxy is replace with a lorem ipsum paragraph
    '''
    
    def __init__ (self, mbox_file, nmbox_file):
        '''
        Constructor
        '''
        self.src_mbox           = mailbox.mbox(mbox_file)
        self.dest_mbox          = mailbox.mbox(nmbox_file, create=True)
        self.faker              = Faker()
        self.name_emails        = {}


    def anonomize (self, pii):
        '''
        Creates fake names and name_emails
        Checks to see if the name has already been given a fake name
        '''
        name = pii[:pii.find('<')].strip()

        if name in self.name_emails.keys():
            fakename, email = self.name_emails[name]
        else:
            fakename = self.faker.name()
            email    = self.faker.email()
            self.name_emails[name] = (fakename,email)
        return '%s <%s>' % (fakename,email)


    def extract_time (self, header):
        '''
        Extract the time from the header
        '''
        try:
            time_str = header[header.find(' '):].strip()
            return strptime(time_str, '%a %b %d %H:%M:%S %Y')
        except:
            return gmtime()


    def create (self):
        '''
        Loop through source emails and construct a fake email
        '''
        try:
            self.src_mbox.lock()
            self.dest_mbox.lock()

            for msg in self.src_mbox:
                fmsg = mailbox.mboxMessage()
                fmsg.set_from('MAILER-DAEMON',time_=self.extract_time(msg.get_from()))
                for k,v in msg.items():
                    if k in ('To', 'From'):
                        fmsg[k] = self.anonomize(v)
                    elif k =='Subject':
                        fmsg[k] = self.faker.company()
                    fmsg.set_payload(generate_paragraph()[-1])
                self.dest_mbox.add(fmsg)
                self.dest_mbox.flush()
        finally:
            self.src_mbox.unlock()
            self.src_mbox.close()
            self.dest_mbox.unlock()
            self.dest_mbox.close()
        


if __name__ == '__main__':
    src_mbox = sys.argv[1]
    dest_mbox = sys.argv[2]
    mbx = FakeMbox(src_mbox, dest_mbox)
    mbx.create()
