#!/usr/bin/env python3

from docopt import docopt
from methods import (
    get_assembly_plan_from_sbol,
    compute_all_construct_quotes,
    write_output_spreadsheet,
)
import logging


###################################################################################
#################################### Processify ###################################
###################################################################################

import inspect
import traceback
import sys

from functools import wraps
from multiprocessing import Process, Queue


class Sentinel:
    pass


def processify(func):
    '''Decorator to run a function as a process.
    Be sure that every argument and the return value
    is *pickable*.
    The created process is joined, so the code does not
    run in parallel.
    '''

    def process_generator_func(q, *args, **kwargs):
        result = None
        error = None
        it = iter(func())
        while error is None and result != Sentinel:
            try:
                result = next(it)
                error = None
            except StopIteration:
                result = Sentinel
                error = None
            except Exception:
                ex_type, ex_value, tb = sys.exc_info()
                error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
                result = None
            q.put((result, error))

    def process_func(q, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception:
            ex_type, ex_value, tb = sys.exc_info()
            error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
            result = None
        else:
            error = None

        q.put((result, error))

    def wrap_func(*args, **kwargs):
        # register original function with different name
        # in sys.modules so it is pickable
        process_func.__name__ = func.__name__ + 'processify_func'
        setattr(sys.modules[__name__], process_func.__name__, process_func)

        q = Queue()
        p = Process(target=process_func, args=[q] + list(args), kwargs=kwargs)
        p.start()
        result, error = q.get()
        p.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = '%s (in subprocess)\n%s' % (str(ex_value), tb_str)
            raise ex_type(message)

        return result

    def wrap_generator_func(*args, **kwargs):
        # register original function with different name
        # in sys.modules so it is pickable
        process_generator_func.__name__ = func.__name__ + 'processify_generator_func'
        setattr(sys.modules[__name__], process_generator_func.__name__, process_generator_func)

        q = Queue()
        p = Process(target=process_generator_func, args=[q] + list(args), kwargs=kwargs)
        p.start()

        result = None
        error = None
        while error is None:
            result, error = q.get()
            if result == Sentinel:
                break
            yield result
        p.join()

        if error:
            ex_type, ex_value, tb_str = error
            message = '%s (in subprocess)\n%s' % (str(ex_value), tb_str)
            raise ex_type(message)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if inspect.isgeneratorfunction(func):
            return wrap_generator_func(*args, **kwargs)
        else:
            return wrap_func(*args, **kwargs)
    return wrapper


#########################################################################################
################################### DNA Weaver ##########################################
#########################################################################################

#@processify
def runDNAWeaver(inputSBOL_path, outpoutXLSX_path, assembly_method='any_method', max_constructs=None):
    if not assembly_method in ['gibson', 'golden_gate', 'any_method']:
        logging.warning('Did not resognise assembly method input: '+str(assembly_method)+'. Reverting to any_method')
        assembly_method = 'any_method'
    # PARSE THE SBOL FILE
    part_sequences, construct_parts, construct_sequences = get_assembly_plan_from_sbol(path=inputSBOL_path)
    # COMPUTE ALL QUOTES
    quotes, primer_sequences, fragment_quotes, errors = compute_all_construct_quotes(
                                                    construct_sequences=construct_sequences,
                                                    part_sequences=part_sequences,
                                                    assembly_method=assembly_method,
                                                    max_constructs=int(max_constructs) if max_constructs else None)
    # WRITE THE RESULT
    write_output_spreadsheet(quotes=quotes,
                            primer_sequences=primer_sequences,
                            part_sequences=part_sequences,
                            fragment_quotes=fragment_quotes,
                            construct_parts=construct_parts,
                            construct_sequences=construct_sequences,
                            errors=errors,
                            target=outpoutXLSX_path)
    return True
