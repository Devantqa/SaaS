import traceback

class Stepper:
    """
    Wrap any action in stepper.step("Title", lambda: <do something>).
    It always logs the step and attaches a screenshot:
      - On success: "PASSED: Title"
      - On failure: "FAILED: Title" + exception message in report, then re-raises
    """
    def __init__(self, shots, report_pdf=None, report_docx=None):
        self.shots = shots                  # ScreenshotHelper (embeds into DOCX)
        self.report_pdf = report_pdf        # PdfReport or None
        self.report_docx = report_docx      # DocxReport or None

    def _write_reports(self, title, description=None, screenshot_path=None, passed=True):
        status = "PASSED" if passed else "FAILED"
        # DOCX is already updated by ScreenshotHelper via shots.capture()
        # Add a line to PDF report as well
        if self.report_pdf:
            body = description or ""
            self.report_pdf.add_step(f"{status}: {title}", body, screenshot_path=screenshot_path)

    def step(self, title, action=None, description=None):
        """
        Run an action and capture a screenshot (even on failure).
        Returns the action result (if any). Re-raises exceptions after logging.
        """
        try:
            result = action() if action else None
            shot = self.shots.capture(f"{title}")
            self._write_reports(title, description=description, screenshot_path=shot, passed=True)
            return result
        except Exception as e:
            # Capture failure screenshot + full traceback
            tb = traceback.format_exc()
            shot = self.shots.capture(f"FAILED - {title}")
            # Add detailed info to PDF/DOCX
            fail_desc = (description + "\n\n" if description else "") + f"ERROR: {e}\n\n{tb}"
            self._write_reports(title, description=fail_desc, screenshot_path=shot, passed=False)
            raise