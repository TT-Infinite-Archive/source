#!/usr/bin/env python2
import requests
import getpass
import compiler
import json


# Constants:
USER_AGENT = 'RPC Terminal (Toontown Infinite; src)'

URL_API_AUTH_TOKEN_GET = 'https://toontowninfinite.com/api/auth/token/get/'
URL_API_RPC = 'https://toontowninfinite.com/api/rpc/'

service = None
while service not in ('maintenance', 'game'):
    if service is not None:
        print('Invalid service.')
    service = input('Enter service: ')

distribution = None
while distribution not in ('qa', 'test', 'live'):
    if distribution is not None:
        print('Invalid distribution.')
    distribution = input('Enter distribution: ')

api_token = None
while api_token is None:
    username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    if (not username) or (not password):
        print('Missing required login credentials.')
        continue
    payload = {'username': username, 'password': password}
    headers = {'User-Agent': USER_AGENT}
    response = requests.post(URL_API_AUTH_TOKEN_GET, data=payload, headers=headers).json()
    if 'non_field_errors' in response:
        for error in response['non_field_errors']:
            print(error)
    else:
        api_token = response['token']

session = requests.Session()
session.headers.update({'User-Agent': USER_AGENT, 'Authorization': 'Token ' + api_token})


def parse_rpc_method_call(module):
    stmt = module.node
    if not isinstance(stmt, compiler.ast.Stmt):
        raise SyntaxError('unexpected syntax for RPC method call')

    discard = stmt.nodes[0]
    if not isinstance(discard, compiler.ast.Discard):
        raise SyntaxError('unexpected syntax for RPC method call')

    write_mode = None
    write_path = None
    call_func = discard.getChildNodes()[0]
    if not isinstance(call_func, compiler.ast.CallFunc):
        if isinstance(call_func, compiler.ast.Compare):
            op = call_func.ops[0]
            if op[0] != '>':
                raise SyntaxError('unexpected syntax for RPC method call')
            write_mode = 'w'
            const = op[1]
            call_func = call_func.expr
        elif isinstance(call_func, compiler.ast.RightShift):
            write_mode = 'a'
            const = call_func.right
            call_func = call_func.left
        else:
            raise SyntaxError('unexpected syntax for RPC method call')
        if not isinstance(const, compiler.ast.Const):
            raise SyntaxError('unexpected syntax for RPC method call')
        write_path = const.value
        if not isinstance(write_path, str):
            raise SyntaxError('unexpected syntax for RPC method call')

    const_count = 0
    keyword_count = 0
    for arg in call_func.args:
        if not isinstance(arg, (compiler.ast.Const, compiler.ast.Keyword)):
            raise TypeError('invalid argument type: ' + str(type(arg)))
        if isinstance(arg, compiler.ast.Keyword):
            if not isinstance(arg.expr, compiler.ast.Const):
                raise TypeError('invalid argument type: ' + str(type(arg.expr)))
            if const_count > 0:
                raise SyntaxError('cannot use both positional and keyword arguments')
            keyword_count += 1
        if isinstance(arg, compiler.ast.Const):
            if keyword_count > 0:
                raise SyntaxError('cannot use both positional and keyword arguments')
            const_count += 1

    params = []
    if const_count > 0:
        params = [a.value for a in call_func.args]
    elif keyword_count > 0:
        params = dict((a.name, a.expr.value) for a in call_func.args)

    return (call_func.node.name, params, write_mode, write_path)


while True:
    try:
        module = compiler.parse(input('$ '))
        method, params, write_mode, write_path = parse_rpc_method_call(module)
        payload = {'service': service, 'distribution': distribution, 'method': method,
                   'params': json.dumps(params)}
        response = session.post(URL_API_RPC, data=payload).json()
        error = response.get('error')
        if error is not None:
            print('RPC method call resulted in error: %d\n%s' % (error[0], error[1].strip()))
        else:
            result = json.dumps(response['result'], indent=4)
            if write_mode is not None:
                with open(write_path, write_mode) as f:
                    f.write(result + '\n')
            else:
                print(result)
    except (SyntaxError, TypeError, ValueError) as e:
        print('Error while parsing RPC method call:\n', e)
    except IndexError:
        pass
