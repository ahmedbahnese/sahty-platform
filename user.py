from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    نموذج قاعدة البيانات للمستخدمين.

    يمثل جدول المستخدمين في قاعدة البيانات ويحتوي على معلومات أساسية عن المستخدمين.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        """
        يمثل كائن المستخدم كسلسلة نصية.

        Returns:
            str: تمثيل نصي لكائن المستخدم.
        """
        return f\'<User {self.username}>\'

    def to_dict(self):
        """
        يحول كائن المستخدم إلى قاموس (dictionary).

        Returns:
            dict: قاموس يحتوي على معرف المستخدم، اسم المستخدم، والبريد الإلكتروني.
        """
        return {
            \"id\": self.id,
            \"username\": self.username,
            \"email\": self.email
        }


