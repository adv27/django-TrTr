def get_values_recursive(obj):

    if not isinstance(obj,str):
        T = ''
        for v in (obj.values() if isinstance(obj, dict) else obj):
            if v is None: continue
            p = get_values_recursive(v)
            if p is not None:
                T += p
        return T

    if not obj.isdigit() and len(obj) > 10:
        return obj+'\n'
    else:
        return None