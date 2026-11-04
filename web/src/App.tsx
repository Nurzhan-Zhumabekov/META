import { Route, Routes } from "react-router-dom";
import { useApp } from "./lib/context";
import { EmptyState } from "./components/Common";
import { Feed } from "./components/Feed";
import { Profile } from "./components/Profile";
import { ReportDialog } from "./components/Report";
import { Review } from "./components/Review";
import { Shell } from "./components/Shell";
import { Explore, Messages, Reels } from "./components/SocialViews";

export default function App() {
  const { report, setReport } = useApp();
  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>
      <Shell>
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/profile/:handle" element={<Profile />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/reels" element={<Reels />} />
          <Route path="/messages/:handle?" element={<Messages />} />
          <Route path="/saved" element={<Feed savedOnly />} />
          <Route path="/review" element={<Review />} />
          <Route
            path="*"
            element={
              <EmptyState icon="search" title="Page not found">
                Choose a section from the Instagram menu.
              </EmptyState>
            }
          />
        </Routes>
      </Shell>
      {report && (
        <ReportDialog
          key={report.handle}
          account={report}
          onClose={() => setReport(null)}
        />
      )}
    </>
  );
}
