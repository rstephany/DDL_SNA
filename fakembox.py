'''
    __author__  = Ryan Stephany
    __date__    = 11Nov2014
    __owner__   = District Data Labs
    __purpose__ = SNA Workshop
'''

import re
import sys
import mailbox
from faker import Faker
from numpy.random import randint
from time import strptime, gmtime
from loremipsum import get_sentences, generate_paragraph



class FakeMbox (object):
    ''' 
        This is a class that generates a very simple fake mbox
        Most of the email metadata information is not kept
        Email addresses are replaced with fake addresses but still retaining the same domain
        Subject is replace with a fake company
        Body is replace with a lorem ipsum paragraph
    '''
    
    def __init__ (self, mbox_file, nmbox_file):
        '''
        Constructor
        '''
        self.src_mbox           = mailbox.mbox(mbox_file)
        self.dest_mbox          = mailbox.mbox(nmbox_file, create=True)
        self.faker              = Faker()
        self.emails_name        = {}
        self.domains            = {}
        self.re_email = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')


    def anonomize (self, pii):
        '''
        Creates fake names and name_emails
        Checks to see if the name has already been given a fake name
        '''
        emails = self.re_email.findall(pii)
        email_list = []

        for email in emails:
            domain = email.split('@')[-1].strip()
            if domain in self.domains.keys():
                domain = self.domains[domain]
            else:
                domain = self.domains[domain] = '%s.com' % self.faker.company().replace(' ','_')

            if email in self.emails_name.keys():
                fakeemail, fakename = self.emails_name[email]
            else:
                fakename = self.faker.name()
                fakeemail = '%s@%s' % (self.faker.username(), domain)
                self.emails_name[email] = (fakeemail, fakename)

            email_list.append('%s <%s>' % (fakename,fakeemail))
        return ', '.join(email_list)


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
                    if k in ('To', 'From', 'Cc'):
                        fmsg[k] = self.anonomize(v)
                    elif k =='Subject':
                        fmsg[k] = self.faker.company()
                    elif k == 'Date':
                        fmsg[k] = v
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
