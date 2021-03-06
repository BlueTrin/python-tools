import pickle
import logging
import datetime
import time
import csv
import os
import collections

################################################################################

def serialise_obj(obj, filename):
    '''
    Use pickle to store obj in binary format in target filename
    '''
    logging.debug('Serialising object to file ' + filename)
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def deserialise_obj(filename):
    '''
    Use pickle to deserialise object that's been saved in binary format
    '''
    logging.debug('Deserialising object from file ' + filename)
    with open(filename, 'rb') as f:
        return pickle.load(f)

################################################################################

def flatten(seq):
    for x in seq:
        try:
            if isinstance(x, basestring):
                yield x  # not iterable
            else:
                for y in flatten(x):
                    yield y
        except TypeError:
            yield x  # not iterable


def serialise_csv(obj, filename):
    if not os.path.isfile(filename):
        logging.debug('Serialising object to CSV file ' + filename)
        with open(filename, 'wb') as csvfile:
            csvwr = csv.writer(csvfile, quoting=csv.QUOTE_ALL, dialect='excel')
            for line in obj:
                csvwr.writerow(list(flatten(line)))

################################################################################

def log_entry(f): 
    ''' 
    Decorator for functions to log entry 
    ''' 

    def log_entry(*args): 
        logging.debug('.'.join([f.__module__, f.__name__])) 
        return f(*args) 
                    
    log_entry.__name__ = f.__name__ 
    return log_entry

def log_time(f):
    '''
    Decorator to time the function call
    '''
    def wrap(*args):
        with Timer() as t: res = f(*args)
        logging.debug('{0}: {1} ms'.format(f.func_name, t.interval*1000.0))
        return res

    wrap.__name__ = f.__name__
    return wrap
    
################################################################################

class Timer:    
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start

################################################################################

def offset(dte, off, period='BD'):
    '''
    Offset the input date (a datetime.datetime object) by the amount off
    where the period can be
        BD - business days
        M - months
        Y - years
    '''

    def apply_offset():
        period_uc = period.upper()
        if period_uc == 'BD':
            week_offset = off // 5
            days_offset = off % 5
            return dte + datetime.timedelta(days=days_offset, weeks=week_offset)
        elif period_uc == 'M':
            return datetime.datetime(dte.year, dte.month + off, dte.day)
        elif period_uc == 'Y':
            return datetime.datetime(dte.year + off, dte.month, dte.day)
        else:
            raise ValueError('Unrecognised period "{0}" in offset function. Use "BD", "M" or "Y"'.format(period))

    def bridge_weekend(dte, day_of_week):
        if off > 0:
            if day_of_week == 5: return dte + datetime.timedelta(days=2)
            if day_of_week == 6: return dte + datetime.timedelta(days=1)
        if off < 0:
            if day_of_week == 5: return dte + datetime.timedelta(days=-1)
            if day_of_week == 6: return dte + datetime.timedelta(days=-2)
        # If the offset is zero, or the day of the week is not a saturday or
        # a sunday, do not adjust. This is just because the direction of 
        # adjustment isn't obvious
        return dte

    newdate = apply_offset()

    day_of_week = newdate.weekday()
    if day_of_week in [5, 6]: 
        newdate = bridge_weekend(newdate, day_of_week)

    return newdate

################################################################################
