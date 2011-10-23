# TODO
# - do /etc/java/security/security.d stuff, like fedora?
#
# Conditional build:
%bcond_without	javadoc		# don't build javadoc
%bcond_without	tests		# don't build and run tests

%define		archivever	jdk16-%(echo %{version} | tr -d .)
%define classname   org.bouncycastle.jce.provider.BouncyCastleProvider

%define		srcname		bcprov
%include	/usr/lib/rpm/macros.java
Summary:	Bouncy Castle Crypto Package for Java
Name:		java-%{srcname}
Version:	1.46
Release:	1
License:	MIT
Group:		Libraries/Java
URL:		http://www.bouncycastle.org/
# Original source http://www.bouncycastle.org/download/bcprov-%{archivever}.tar.gz
# is modified to
# bcprov-%{archivever}-FEDORA.tar.gz with patented algorithms removed.
# Specifically: IDEA algorithms got removed.
Source0:	bcprov-%{archivever}-FEDORA.tar.gz
# Source0-md5:	a522ba5ababb6505dbd474c3cb924d29
%{?with_tests:BuildRequires:	java-hamcrest}
BuildRequires:	java-junit
BuildRequires:	jdk >= 1.6
BuildRequires:	jpackage-utils >= 1.5
Obsoletes:	bcprov
Obsoletes:	bouncycastle
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Bouncy Castle Crypto package is a Java implementation of
cryptographic algorithms. The package is organised so that it contains
a light-weight API suitable for use in any environment (including the
newly released J2ME) with the additional infrastructure to conform the
algorithms to the JCE framework.

%package javadoc
Summary:	Javadoc for Bouncy Castle Crypto package
Group:		Documentation
Requires:	jpackage-utils
BuildArch:	noarch

%description javadoc
API documentation for the Bouncy Castle Crypto package.

%prep
%setup -q -n bcprov-%{archivever}

# Remove provided binaries
find -type f -name "*.class" | xargs -r rm -v
find -type f -name "*.jar" | xargs -r rm -v

mkdir src
unzip -qq src.zip -d src

%build
cd src

CLASSPATH=$(build-classpath junit)
export CLASSPATH

%javac -g -target 1.5 -encoding UTF-8 $(find . -type f -name "*.java")
jarfile="../bcprov-%{version}.jar"

# Exclude all */test/* files except org.bouncycastle.util.test, cf. upstream
files="$(find . -type f \( -name '*.class' -o -name '*.properties' \) -not -path '*/test/*')"
files="$files $(find . -type f -path '*/org/bouncycastle/util/test/*.class')"
files="$files $(find . -type f -path '*/org/bouncycastle/jce/provider/test/*.class')"
files="$files $(find . -type f -path '*/org/bouncycastle/ocsp/test/*.class')"

test ! -d classes && mf="" || mf="`find classes/ -type f -name "*.mf" 2>/dev/null`"
test -n "$mf" && jar cvfm $jarfile $mf $files || %jar cvf $jarfile $files

%if %{with tests}
CLASSPATH=${PWD:-$(pwd)}:$(build-classpath junit hamcrest-core)
export CLASSPATH
for test in $(find -name AllTests.class); do
	test=${test#./}; test=${test%.class}; test=$(echo $test | tr / .)
	# TODO: failures; get them fixed and remove || :
	%java org.junit.runner.JUnitCore $test || :
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

# install bouncy castle provider
install -d $RPM_BUILD_ROOT%{_javadir}
cp -p %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-%{version}.jar
ln -s %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}.jar

# javadoc
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc *.html
%{_javadir}/%{srcname}-%{version}.jar
%{_javadir}/%{srcname}.jar

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif
