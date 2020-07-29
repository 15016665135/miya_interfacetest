def resp_handle(result_str):
    '''简单检查返回结果，无错误信息代表通过'''
    err_msg = eval(result_str.replace("null", "None").replace("true", "True").replace("false", "False"))[0]["err"]
    if "<nil>" in err_msg:
        return True
    else:
        return False