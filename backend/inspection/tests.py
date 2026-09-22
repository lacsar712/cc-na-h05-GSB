from django.contrib.auth.models import Group, User
from django.test import TestCase

from inspection.display import present_detail, present_list
from inspection.models import Inspection


class ColumnAlignmentTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="inspector")
        self.keeper = User.objects.create_user(username="keeper", password="x")
        self.keeper.groups.add(self.group)
        self.watch = User.objects.create_user(username="watch", password="x")

    def test_submitted_values_stored_in_their_own_columns(self):
        self.client.force_login(self.keeper)
        resp = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-T1",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "0.4",
            },
        )
        self.assertEqual(resp.status_code, 302)

        row = Inspection.objects.get(aid_code="LH-T1")
        # 登记页提交的两个数原样落库，不得对调
        self.assertAlmostEqual(row.measured_cd, 1400.0)
        self.assertAlmostEqual(row.bearing_error_deg, 0.4)

        listed = present_list(row)
        self.assertEqual(listed["candela_cell"], "1400.0")
        self.assertEqual(listed["angle_cell"], "0.4")

        detail = present_detail(row)
        self.assertEqual(detail["candela_cell"], "1400.0")
        self.assertEqual(detail["angle_cell"], "0.4")

    def test_list_and_detail_pages_render_columns_in_order(self):
        self.client.force_login(self.keeper)
        self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-T2",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "0.4",
            },
        )
        row = Inspection.objects.get(aid_code="LH-T2")

        listing = self.client.get("/").content.decode()
        c = listing.index("1400.0")
        a = listing.index("0.4")
        self.assertLess(c, a, "总表光强列必须在方位列之前，两列不得对调")

        detail = self.client.get(f"/inspections/{row.pk}/").content.decode()
        self.assertIn("实测光强 1400.0", detail)
        self.assertIn("方位偏差 0.4 度", detail)

    def test_readonly_account_kept_readonly(self):
        self.assertFalse(self.watch.groups.filter(name="inspector").exists())
        self.client.force_login(self.watch)

        self.assertEqual(self.client.get("/").status_code, 200)
        # 只读账号既看不到登记表单，也无法借 POST 写入
        self.assertEqual(self.client.get("/inspections/new/").status_code, 403)
        self.assertEqual(
            self.client.post(
                "/inspections/new/",
                {
                    "aid_code": "LH-X",
                    "measured_cd": "1400",
                    "required_cd": "1200",
                    "bearing_error_deg": "0.4",
                },
            ).status_code,
            403,
        )
        self.assertEqual(Inspection.objects.count(), 0)
