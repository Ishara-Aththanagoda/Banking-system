from datetime import datetime
from . import db

# Log an audit action
def log_audit(action, collection_name, document_id, user_id):
    audit_log = {
        "action": action,
        "collection": collection_name,
        "documentId": document_id,
        "userId": user_id,
        "timestamp": datetime.now()
    }
    db.audit_logs.insert_one(audit_log)
