import logging
from ldap3 import Server, Connection, SUBTREE
from flask import current_app

logger = logging.getLogger(__name__)


class LdapService:
    """AD LDAP 인증 서비스 (leemock.local)"""

    def _get_server(self):
        return Server(current_app.config['LDAP_SERVER'])

    def authenticate(self, username: str, password: str) -> tuple[bool, dict | str]:
        """
        AD 인증 수행
        Returns: (True, user_info_dict) 또는 (False, error_message)
        """
        if current_app.config.get('LDAP_MOCK_MODE'):
            return self._mock_authenticate(username, password)

        try:
            server = self._get_server()

            # 1단계: 서비스 계정으로 바인드
            try:
                conn = Connection(
                    server,
                    user=current_app.config['LDAP_BIND_USER_DN'],
                    password=current_app.config['LDAP_BIND_USER_PASSWORD'],
                    auto_bind=True
                )
            except Exception as e:
                logger.error(f"LDAP bind failed: {e}")
                return False, "LDAP 서버 연결에 실패했습니다."

            # 2단계: 사용자 검색
            conn.search(
                search_base=current_app.config['LDAP_BASE_DN'],
                search_filter=f'(sAMAccountName={username})',
                search_scope=SUBTREE,
                attributes=['distinguishedName', 'displayName', 'mail',
                            'sAMAccountName', 'department', 'title']
            )

            if not conn.entries:
                conn.unbind()
                logger.warning(f"LDAP user not found: {username}")
                return False, "사용자 ID를 찾을 수 없습니다."

            entry = conn.entries[0]
            user_dn = entry.entry_dn
            display_name = str(entry.displayName) if entry.displayName else username
            email = str(entry.mail) if entry.mail else None
            department = str(entry.department) if entry.department else None
            position = str(entry.title) if entry.title else None
            conn.unbind()

            # 3단계: 사용자 비밀번호로 인증
            try:
                user_conn = Connection(server, user=user_dn, password=password, auto_bind=True)
                user_conn.unbind()
            except Exception as e:
                logger.warning(f"LDAP password auth failed for {username}: {e}")
                return False, "비밀번호가 올바르지 않습니다."

            user_info = {
                'username': username,
                'display_name': display_name,
                'email': email,
                'department': department,
                'position': position,
            }
            logger.info(f"LDAP auth success: {username}")
            return True, user_info

        except Exception as e:
            logger.error(f"Unexpected LDAP error for {username}: {e}")
            return False, "인증 중 오류가 발생했습니다."

    def _mock_authenticate(self, username: str, password: str) -> tuple[bool, dict | str]:
        """개발/테스트용 Mock 인증"""
        mock_users = {
            'admin':  {'password': 'admin123',  'display_name': '관리자',  'department': '전산팀', 'email': 'admin@leemock.com', 'position': '팀장'},
            'tester': {'password': 'test123',   'display_name': '테스터',  'department': '전산팀', 'email': 'test@leemock.com',  'position': '사원'},
        }
        user = mock_users.get(username)
        if user and user['password'] == password:
            return True, {
                'username': username,
                'display_name': user['display_name'],
                'email': user['email'],
                'department': user['department'],
                'position': user['position'],
            }
        return False, "아이디 또는 비밀번호가 일치하지 않습니다."


ldap_service = LdapService()
