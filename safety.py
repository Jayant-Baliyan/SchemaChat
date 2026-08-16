import re
DANGEROUS_KEYWORDS=[
    "DROP","DELETE","ALTER","UPDATE","INSERT","TRUNCATE","CREATE","REPLACE","GRANT","REVOKE","EXEC","EXECUTE","PRAGMA","ATTACH","DETACH","VACUUM","RENAME","MERGE","CALL","SET","COPY","LOCK","COMMENT","RESTORE","KILL"]

def is_safe_query(sql:str)->tuple[bool,str]:
    if not sql or not isinstance(sql,str):
        return False,"Empty or invalid query"

    cleaned=sql.upper().strip()
    cleaned=re.sub(r'--.*$','',cleaned,flags=re.MULTILINE)
    cleaned=re.sub(r'/\*.*?\*/','',cleaned,flags=re.DOTALL)
    cleaned=cleaned.strip()

    if not cleaned:
        return False,"Query is empty after removing comments"

    if not cleaned.startswith("SELECT"):
        return False,"Only SELECT queries are allowed"

    for keyword in DANGEROUS_KEYWORDS:
        pattern=r'\b'+keyword+r'\b'
        if re.search(pattern, cleaned):
            return False,f"Query contains dangerous keyword: {keyword}"
        
    return True,"Query is safe"


def sanitize_input(user_input:str)->str:
    had_comment='--' in user_input or ('/*' in user_input and '*/' in user_input)

    cleaned=re.sub(r'--.*$','',user_input,flags=re.MULTILINE)
    cleaned=re.sub(r'/\*.*?\*/','',cleaned,flags=re.DOTALL)

    if had_comment:
        dangerous_pattern=r"\b("+'|'.join(DANGEROUS_KEYWORDS)+r")\b"
        if re.search(dangerous_pattern,cleaned.upper()):
            return "I cannot process request containing SQL comment patterns."

    return cleaned.strip()

if __name__=="__main__":
    test_cases=[
        ("SELECT * FROM customers",True),
        ("select count(*) from orders",True),
        ("   SELECT * FROM users   ",True),

        ("DROP TABLE customers", False),
        ("DELETE FROM users", False),
        ("UPDATE users SET admin=1", False),
        ("INSERT INTO users VALUES (1)", False),
        ("SELECT * FROM users; DROP TABLE users", False),
        ("", False),
        ("ALTER TABLE users ADD COLUMN age", False)
    ]
    print("Testin is_safe_query():")
    print('='*50)
    for sql, expected_safe in test_cases:
        is_safe,reason=is_safe_query(sql)
        status="PASS" if is_safe==expected_safe else "FAIL"
        print(f"{status} | is_safe={is_safe} | {sql[:50]}" )
        if not is_safe:
            print(f"Reason: {reason}")

    print("\nTesting sanitise_input():")
    print('='*50)
    dirty_inputs=["Show me customers -- and DROP TABLE users",
        "List orders /* DELETE FROM */ please",
        "  Normal question  ",
        "DR/* */OP TABLE users",
        ]
    for dirty in dirty_inputs:
        clean=sanitize_input(dirty)
        print(f"Before: {dirty}")
        print(f"After: {clean}")
        print()

    attack_cases=[("DR/* */OP TABLE users", "Should be neutralized"),
        ("DELETE/*comment*/ FROM users", "Should be neutralized"),
        ("Show me customers -- and DROP TABLE", "Should be neutralized"),
        ("Normal question about sales", "Should pass through"),
        ("How do I update my profile?", "Should pass through (no comments)")]
    for user_input, expected in attack_cases: 
        result=sanitize_input(user_input)
        is_blocked="cannot process" in result
        status="Blocked" if is_blocked else "Allowed"
        print(f"{status} | Input: {user_input[:]}")
        print(f"         Output: {result[:50]}")
        print()
