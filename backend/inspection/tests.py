from django.contrib.auth.models import Group, User
from django.test import TestCase

from inspection.models import Inspection
from inspection.presentation import present_detail, present_list


class ColumnAlignmentTests(TestCase):
    """光强（坎德拉）与方位偏差（度）必须各走各的列，不得对调。"""

    def setUp(self):
        inspectors = Group.objects.create(name="inspector")
        self.keeper = User.objects.create_user(username="keeper", password="x")
        self.keeper.groups.add(inspectors)
        self.watch = User.objects.create_user(username="watch", password="x")

    def _submit(self):
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-01",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "0.4",
            },
        )
        return response

    def test_submitted_values_land_in_their_own_columns(self):
        self.client.force_login(self.keeper)
        response = self._submit()

        row = Inspection.objects.get(aid_code="LH-01")
        self.assertEqual(row.measured_cd, 1400.0)
        self.assertEqual(row.bearing_error_deg, 0.4)

        # 提交后跳转的详情页：光强列显示坎德拉、方位列显示度
        detail = self.client.get(response.url).content.decode()
        self.assertIn("实测光强 1400.0", detail)
        self.assertIn("方位偏差 0.4 度", detail)
        self.assertNotIn("实测光强 0.4", detail)
        self.assertNotIn("方位偏差 1400.0", detail)

        # 总表同样不得对调
        listing = self.client.get("/").content.decode()
        self.assertIn("<td>1400.0</td>", listing)
        self.assertIn("<td>0.4</td>", listing)

    def test_list_cells_are_not_swapped(self):
        row = Inspection.objects.create(
            aid_code="LH-01",
            measured_cd=1400.0,
            required_cd=1200.0,
            bearing_error_deg=0.4,
            verdict="合格",
            note="光强与方位均在限内",
            created_by="keeper",
        )

        shown = present_list(row)
        self.assertEqual(shown["candela_cell"], "1400.0")
        self.assertEqual(shown["angle_cell"], "0.4")

    def test_detail_cells_are_not_swapped(self):
        row = Inspection.objects.create(
            aid_code="LH-01",
            measured_cd=1400.0,
            required_cd=1200.0,
            bearing_error_deg=0.4,
            verdict="合格",
            note="光强与方位均在限内",
            created_by="keeper",
        )

        shown = present_detail(row)
        self.assertEqual(shown["candela_cell"], "1400.0")
        self.assertEqual(shown["angle_cell"], "0.4")

    def test_rendered_list_puts_values_in_matching_columns(self):
        self.client.force_login(self.keeper)
        Inspection.objects.create(
            aid_code="LH-01",
            measured_cd=1400.0,
            required_cd=1200.0,
            bearing_error_deg=0.4,
            verdict="合格",
            note="",
            created_by="keeper",
        )

        body = self.client.get("/").content.decode()
        tbody = body.split("<tbody>")[1].split("</tbody>")[0]
        row_html = tbody.split("<tr>")[1].split("</tr>")[0]
        cells = [
            part.split(">", 1)[1].strip()
            for part in row_html.split("</td>")[:-1]
        ]
        self.assertEqual(cells[0], "LH-01")
        self.assertEqual(cells[1], "1400.0")
        self.assertEqual(cells[2], "0.4")

    def test_rendered_detail_puts_values_in_matching_columns(self):
        self.client.force_login(self.keeper)
        row = Inspection.objects.create(
            aid_code="LH-01",
            measured_cd=1400.0,
            required_cd=1200.0,
            bearing_error_deg=0.4,
            verdict="合格",
            note="",
            created_by="keeper",
        )

        body = self.client.get(f"/inspections/{row.pk}/").content.decode()
        self.assertIn("实测光强 1400.0", body)
        self.assertIn("方位偏差 0.4 度", body)
        self.assertNotIn("实测光强 0.4", body)
        self.assertNotIn("方位偏差 1400.0", body)


class ReadOnlyAccountTests(TestCase):
    """只读账号（不在 inspector 组）不得借任何改动获得写入能力。"""

    def setUp(self):
        self.keeper = User.objects.create_user(username="keeper", password="x")
        self.keeper.groups.create(name="inspector")
        self.keeper.groups.add(Group.objects.get(name="inspector"))
        self.watch = User.objects.create_user(username="watch", password="x")

    def test_readonly_gets_403_on_form_and_submission(self):
        self.client.force_login(self.watch)
        self.assertEqual(self.client.get("/inspections/new/").status_code, 403)
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-01",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "0.4",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Inspection.objects.count(), 0)

    def test_inspector_can_still_register(self):
        self.client.force_login(self.keeper)
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-01",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "0.4",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inspection.objects.count(), 1)
