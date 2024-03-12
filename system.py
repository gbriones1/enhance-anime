import functools
import os
import subprocess
import re
import time

def call_subprocess(cmd_list: list, patterns=[], environment=None, quiet=True, pattern_callback=None, callback_conext={}):
        my_env = None
        if environment:
            my_env = os.environ.copy()
            for env_var in environment:
                my_env[env_var] = environment[env_var]
        else:
            environment=None
        print(f'Execute command on system: {" ".join(cmd_list)} with custom environment: {environment}')
        try:
            process = subprocess.Popen(cmd_list, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            subprocess_pid = process.pid
            print(f"Command executed with subprocess PID:{subprocess_pid}")
            while process.poll() is None:
                for line in process.stdout:
                    if not quiet:
                        print("{}".format(line.rstrip().decode("utf-8")))
                    for pattern in patterns:
                        match = re.search(rf'{pattern}', str(line)) 
                        if match:
                            if pattern_callback:
                                pattern_callback(line.rstrip().decode("utf-8"), **callback_conext)
                if process.stderr:
                    for line in process.stderr:
                        if not quiet:
                            print("{}".format(line.rstrip().decode("utf-8")))
                        for pattern in patterns:
                            match = re.search(rf'{pattern}', str(line)) 
                            if match:
                                if pattern_callback:
                                    pattern_callback(line.rstrip().decode("utf-8"), **callback_conext)
            result = process.poll()
            if result != 0:
                raise subprocess.CalledProcessError(result, process.args)
            else: 
                print(f"Process {subprocess_pid} completed...")
                return 0
        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed. Exception: {e}")
            return 1


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug