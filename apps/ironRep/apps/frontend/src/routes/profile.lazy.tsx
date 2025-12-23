import { createLazyFileRoute } from "@tanstack/react-router";
import { UserProfile } from "../features/profile/UserProfile";

export const Route = createLazyFileRoute("/profile")({
  component: ProfilePage,
});

function ProfilePage() {
  return (
    <div className="container mx-auto py-4 sm:py-6 px-3 sm:px-4 pb-24">
      <UserProfile />
    </div>
  );
}
